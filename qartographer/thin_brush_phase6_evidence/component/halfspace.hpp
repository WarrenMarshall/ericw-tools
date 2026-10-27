// Standalone QQBSP Phase 6 experiment. No compiler linkage or geometry mutation.
#pragma once
#include <gmpxx.h>
#include <array>
#include <vector>
#include <optional>
#include <cmath>
#include <limits>
#include <algorithm>
#include <stdexcept>
#include <chrono>
#include <cfenv>
#include <bit>
#include <string>
#include <type_traits>
#if defined(__SSE__)
#include <xmmintrin.h>
#endif

#ifdef __FAST_MATH__
#error "Certified interval filters require strict floating-point semantics"
#endif
static_assert(std::numeric_limits<double>::is_iec559 && std::numeric_limits<double>::digits==53);
namespace p6 {
inline bool environment_ok(){
 if(std::fegetround()!=FE_TONEAREST)return false;
#if defined(__SSE__)
 if(_mm_getcsr() & ((1<<15)|(1<<6)))return false;
#endif
 return true;
}
using Q=mpq_class;
using Plane=std::array<double,4>; // n.x <= d; coefficients are exact binary64 values
struct Stats { size_t fast=0, adaptive=0, exact=0, triples=0, exact_homogeneous_builds=0, exact_rank_constraints=0; bool profile=false; long long worst_sign_ns=0; };
struct SignTimer {
 Stats&s;std::chrono::steady_clock::time_point start;
 explicit SignTimer(Stats&stats):s(stats){if(s.profile)start=std::chrono::steady_clock::now();}
 ~SignTimer(){if(s.profile)s.worst_sign_ns=std::max(s.worst_sign_ns,static_cast<long long>(std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now()-start).count()));}
};
enum class Mode { filtered, double_exact, exact_only };
template<class T> struct I {
 T lo=0,hi=0;
 I()=default;
 explicit I(double v):lo(static_cast<T>(v)),hi(static_cast<T>(v)){}
 I(T a,T b):lo(a),hi(b){}
 static I entire(){return {-std::numeric_limits<T>::infinity(),std::numeric_limits<T>::infinity()};}
 friend I operator-(I a){return {-a.hi,-a.lo};}
 friend I operator+(I a,I b){
  if(a.lo==0 && a.hi==0)return b;
  if(b.lo==0 && b.hi==0)return a;
  if(a.lo==a.hi && b.lo==b.hi && a.lo==-b.lo)return I{};
  // Exact small-integer arithmetic is a structural filter, not a geometry
  // threshold: p-bit binary floats represent every integer through 2^p.
  const T add_limit=std::ldexp(T(1),std::numeric_limits<T>::digits-2);
  if(a.lo==a.hi && b.lo==b.hi && std::abs(a.lo)<=add_limit && std::abs(b.lo)<=add_limit && std::trunc(a.lo)==a.lo && std::trunc(b.lo)==b.lo){T sum=a.lo+b.lo;return {sum,sum};}
  T l=a.lo+b.lo,h=a.hi+b.hi;
  if(!std::isfinite(l)||!std::isfinite(h))return entire();
  return {std::nextafter(l,-std::numeric_limits<T>::infinity()),std::nextafter(h,std::numeric_limits<T>::infinity())};
 }
 friend I operator-(I a,I b){return a+-b;}
 friend I operator*(I a,I b){
  if((a.lo==0&&a.hi==0)||(b.lo==0&&b.hi==0))return I{};
  if(a.lo==1&&a.hi==1)return b;
  if(b.lo==1&&b.hi==1)return a;
  if(a.lo==-1&&a.hi==-1)return -b;
  if(b.lo==-1&&b.hi==-1)return -a;
  const T mul_limit=std::ldexp(T(1),std::numeric_limits<T>::digits/2-1);
  if(a.lo==a.hi && b.lo==b.hi && std::abs(a.lo)<=mul_limit && std::abs(b.lo)<=mul_limit && std::trunc(a.lo)==a.lo && std::trunc(b.lo)==b.lo){T product=a.lo*b.lo;return {product,product};}
  T v[]={a.lo*b.lo,a.lo*b.hi,a.hi*b.lo,a.hi*b.hi};
  for(T x:v)if(!std::isfinite(x))return entire();
  auto mm=std::minmax_element(v,v+4);
  return {std::nextafter(*mm.first,-std::numeric_limits<T>::infinity()),std::nextafter(*mm.second,std::numeric_limits<T>::infinity())};
 }
 std::optional<int> sign()const{
  if(lo>0)return 1;if(hi<0)return -1;if(lo==0&&hi==0)return 0;return {};
 }
};
template<class T> T det(std::array<std::array<T,3>,3> a){
 return a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
       -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
       +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]);
}
template<class T> std::array<T,4> homogeneous(const std::array<Plane,3>& ps){
 std::array<std::array<T,3>,3>a;
 for(int i=0;i<3;++i)for(int j=0;j<3;++j)a[i][j]=T(ps[i][j]);
 std::array<T,4>h;h[3]=det(a);
 for(int k=0;k<3;++k){auto b=a;for(int i=0;i<3;++i)b[i][k]=T(ps[i][3]);h[k]=det(b);}
 return h;
}
template<class T>T residual(const Plane&p,const std::array<T,4>&h){
 return T(p[0])*h[0]+T(p[1])*h[1]+T(p[2])*h[2]-T(p[3])*h[3];
}
inline int qsign(const Q&x){return x>0?1:x<0?-1:0;}
struct Candidate {
 std::array<Plane,3>planes;
 std::optional<std::array<I<double>,4>>d;
 std::optional<std::array<I<long double>,4>>l;
 std::optional<std::array<Q,4>>q;
 std::vector<size_t> incidence;
 Stats&stats;Mode mode;
 Candidate(std::array<Plane,3>p,Stats&s,Mode m):planes(p),stats(s),mode(m){}
 const auto& rational(){if(!q){q=homogeneous<Q>(planes);++stats.exact_homogeneous_builds;}return *q;}
 template<class F,class G>int sign(F interval,G exact){
  SignTimer timer(stats);
  if(mode!=Mode::exact_only){
   if(!d)d=homogeneous<I<double>>(planes);
   if(auto s=interval(*d).sign()){++stats.fast;return *s;}
   if(mode==Mode::filtered){
    if(!l)l=homogeneous<I<long double>>(planes);
    if(auto s=interval(*l).sign()){++stats.adaptive;return *s;}
   }
  }
  ++stats.exact;return qsign(exact(rational()));
 }
 int denominator(){return sign([](auto&h){return h[3];},[](auto&h){return h[3];});}
 int side(const Plane&p,int ds){
  for(auto&support:planes)if(support==p)return 0; // defining incidence, no rounded construction
  return ds*sign([&](auto&h){return residual(p,h);},[&](auto&h)->Q{return residual(p,h);});
 }
};
template<class T>T minor_det(const std::vector<std::array<T,4>>&rows,const std::vector<int>&columns,size_t row=0){
 if(columns.size()==1)return rows[row][columns[0]];
 T sum=T(0.);for(size_t i=0;i<columns.size();++i){auto rest=columns;rest.erase(rest.begin()+i);T term=rows[row][columns[i]]*minor_det(rows,rest,row+1);if(i%2)sum=sum-term;else sum=sum+term;}return sum;
}
struct ProjectiveRank {
 std::vector<Candidate> selected;std::vector<std::vector<size_t>> seen;
 Stats&stats;Mode mode;
 ProjectiveRank(Stats&s,Mode m):stats(s),mode(m){}
 int rank()const{return int(selected.size())-1;}
 bool add(Candidate&v){
  if(std::find(seen.begin(),seen.end(),v.incidence)!=seen.end())return false;
  seen.push_back(v.incidence);
  if(selected.empty()){selected.push_back(v);return true;}
  std::vector<Candidate*>rows;for(auto&r:selected)rows.push_back(&r);rows.push_back(&v);
  auto evaluate=[&]<class T>() -> std::vector<std::array<T,4>>{
   std::vector<std::array<T,4>> hs;
   for(auto*r:rows){if constexpr(std::is_same_v<T,I<double>>){if(!r->d)r->d=homogeneous<I<double>>(r->planes);hs.push_back(*r->d);}
    else if constexpr(std::is_same_v<T,I<long double>>){if(!r->l)r->l=homogeneous<I<long double>>(r->planes);hs.push_back(*r->l);}
    else hs.push_back(r->rational());}return hs;};
  for(int mask=1;mask<16;++mask){if(static_cast<size_t>(std::popcount(static_cast<unsigned>(mask)))!=rows.size())continue;
   std::vector<int>cols;for(int i=0;i<4;++i)if(mask&(1<<i))cols.push_back(i);
   SignTimer timer(stats);
   int sign=0;bool resolved=false;
   if(mode!=Mode::exact_only){if(auto z=minor_det(evaluate.template operator()<I<double>>(),cols).sign()){sign=*z;resolved=true;++stats.fast;}
    if(!resolved&&mode==Mode::filtered)if(auto z=minor_det(evaluate.template operator()<I<long double>>(),cols).sign()){sign=*z;resolved=true;++stats.adaptive;}}
   if(!resolved){++stats.exact;sign=qsign(minor_det(evaluate.template operator()<Q>(),cols));}
   if(sign){selected.push_back(v);return true;}
  }return false;
 }
};

struct Basis {
 std::array<std::array<Q,3>,3>rows{}; std::array<bool,3>used{};int rank=0;
 void add(std::array<Q,3>v){
  for(int i=0;i<3;++i){if(v[i]==0)continue;if(used[i]){Q s=v[i];for(int j=i;j<3;++j)v[j]-=s*rows[i][j];}
   else{Q s=v[i];for(int j=i;j<3;++j)rows[i][j]=v[j]/s;used[i]=true;++rank;return;}}
 }
};
inline Plane opposite(Plane p){for(auto&v:p)v=-v;return p;}
inline bool finite(const std::vector<Plane>&ps){for(auto&p:ps)for(double v:p)if(!std::isfinite(v))return false;return true;}
inline bool axial_enclosure(const std::vector<Plane>&ps){
 bool seen[3][2]={};
 for(auto&p:ps)for(int k=0;k<3;++k)if(p[k]!=0 && p[(k+1)%3]==0 && p[(k+2)%3]==0)seen[k][p[k]>0]=true;
 for(auto&s:seen)if(!s[0]||!s[1])return false;return true;
}
template<class F>bool vertices(const std::vector<Plane>&ps,Stats&stats,Mode mode,F accept){
 for(size_t a=0;a<ps.size();++a)for(size_t b=a+1;b<ps.size();++b)for(size_t c=b+1;c<ps.size();++c){
  ++stats.triples;Candidate v({ps[a],ps[b],ps[c]},stats,mode);int ds=v.denominator();if(!ds)continue;
  bool feasible=true;for(size_t i=0;i<ps.size();++i){int side=v.side(ps[i],ds);if(side>0){feasible=false;break;}if(side==0)v.incidence.push_back(i);}
  if(feasible && accept(v))return true;
 }return false;
}
// A nonzero recession ray can be rescaled into [-1,1]^3. Its intersection
// with that cube is a bounded polytope; a nonzero point implies a nonzero vertex.
inline bool bounded(const std::vector<Plane>&ps,Stats&s,Mode mode){
 if(axial_enclosure(ps))return true;
 std::vector<Plane>cone;for(auto p:ps){p[3]=0;cone.push_back(p);}
 for(int k=0;k<3;++k)for(double sign:{-1.,1.}){Plane p{};p[k]=sign;p[3]=1;cone.push_back(p);}
 bool nonzero=vertices(cone,s,mode,[&](Candidate&v){
  for(int k=0;k<3;++k)if(v.sign([&](auto&h){return h[k];},[&](auto&h){return h[k];}))return true;
  return false;
 });
 return !nonzero;
}
struct Result { int dimension=-2; std::string reason; // -2 Unresolved, -1 Empty, 0..2 LowerDimensional, 3 PositiveVolume
 std::string kind()const{return dimension==-2?"Unresolved":dimension==-1?"Empty":dimension==3?"PositiveVolume":"LowerDimensional";}
};
inline Result analyze(std::vector<Plane>ps,Stats&s,Mode mode=Mode::filtered){
 if(!environment_ok())return {-2,"unsupported arithmetic environment (rounding/FTZ/DAZ)"};
 if(!finite(ps))return {-2,"nonfinite coefficient"};
 if(ps.size()>96)return {-2,"96-constraint experimental resource limit"};
 std::sort(ps.begin(),ps.end());ps.erase(std::unique(ps.begin(),ps.end()),ps.end());
 for(auto&p:ps)if(p[0]==0&&p[1]==0&&p[2]==0&&p[3]<0)return {-1,{}};
 if(!bounded(ps,s,mode))return {-2,"unbounded feasible-set/recession support not in this API"};
 // Exact opposite constraints bound affine dimension before enumerating.
 Basis equalities;for(auto&p:ps)if(std::binary_search(ps.begin(),ps.end(),opposite(p))){++s.exact_rank_constraints;equalities.add({Q(p[0]),Q(p[1]),Q(p[2])});}
 int goal=3-equalities.rank;ProjectiveRank rank(s,mode);
 vertices(ps,s,mode,[&](Candidate&v){rank.add(v);return rank.rank()==goal;});
 if(rank.selected.empty())return {-1,{}};
 return {rank.rank(),{}};
}
// Scalar predicates also support exact plane identity and proposed binary vertices.
inline std::optional<int> point_side(const Plane&p,const std::array<double,3>&x,Stats&s,Mode mode){
 if(!environment_ok() || !finite({p}))return {};
 for(double v:x)if(!std::isfinite(v))return {};
 SignTimer timer(s);
 auto eval=[&]<class T>() ->T{T r=T(0.);for(int i=0;i<3;++i)r=r+T(p[i])*T(x[i]);return r-T(p[3]);};
 if(mode!=Mode::exact_only){if(auto z=eval.template operator()<I<double>>().sign()){++s.fast;return *z;}
  if(mode==Mode::filtered)if(auto z=eval.template operator()<I<long double>>().sign()){++s.adaptive;return *z;}}
 ++s.exact;return qsign(eval.template operator()<Q>());
}
// Scaled equality uses all four exact coefficients. Positive scaling preserves
// a halfspace; negative scaling is the opposing halfspace on the same boundary.
inline std::string relation(const Plane&a,const Plane&b){
 if(!environment_ok() || !finite({a,b}))return "Unresolved";
 int k=-1;for(int i=0;i<3;++i)if(a[i]!=0){k=i;break;}
 if(k<0)return "Degenerate";
 if(b[k]==0)return "Distinct";
 Q scale=Q(b[k])/Q(a[k]);for(int i=0;i<4;++i)if(Q(b[i])!=scale*Q(a[i]))return "Distinct";
 return scale>0?"Equivalent":"Opposing";
}
} // namespace p6
