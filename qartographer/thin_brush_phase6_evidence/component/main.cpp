#include "halfspace.hpp"
#include <nlohmann/json.hpp>
#include <iostream>
#include <fstream>
#include <cstdlib>
#include <cstddef>
#include <new>
#include <cstring>
// Requested allocation accounting for ordinary C++ allocations, including Boost.
struct alignas(std::max_align_t) Allocation { size_t size; };
static size_t calls=0,total_bytes=0,live_bytes=0,peak_bytes=0;
__attribute__((noinline)) void*operator new(size_t n){auto*p=static_cast<Allocation*>(std::malloc(sizeof(Allocation)+n));if(!p)throw std::bad_alloc();p->size=n;++calls;total_bytes+=n;live_bytes+=n;peak_bytes=std::max(peak_bytes,live_bytes);return p+1;}
__attribute__((noinline)) void operator delete(void*p)noexcept{if(p){auto*h=static_cast<Allocation*>(p)-1;live_bytes-=h->size;std::free(h);}}
void operator delete(void*p,size_t)noexcept{::operator delete(p);}
static void* galloc(size_t n){try{return ::operator new(n);}catch(...){std::abort();}}
static void gfree(void*p,size_t){::operator delete(p);}
static void* grealloc(void*p,size_t oldn,size_t n){void*q=galloc(n);if(p)std::memcpy(q,p,std::min(oldn,n));gfree(p,oldn);return q;}
using json=nlohmann::json;
int main(int argc,char**argv){
 try{
  mp_set_memory_functions(galloc,grealloc,gfree);
  if(argc!=3&&argc!=4)throw std::runtime_error("usage: predicate CASES.json filtered|double-exact|exact [--latency]");
  std::string m=argv[2];if(m!="filtered"&&m!="double-exact"&&m!="exact")throw std::runtime_error("unknown mode");p6::Mode mode=m=="filtered"?p6::Mode::filtered:m=="double-exact"?p6::Mode::double_exact:p6::Mode::exact_only;
  std::ifstream in(argv[1]);json cases;in>>cases;json results=json::array();
  for(auto&c:cases){
   p6::Stats stats;stats.profile=argc==4;size_t ac=calls,ab=total_bytes,lb=live_bytes;peak_bytes=live_bytes;
   auto start=std::chrono::steady_clock::now();auto ps=c.at("planes").get<std::vector<p6::Plane>>();
   size_t api_calls=0;double worst_api_us=0;
   auto timed=[&](const std::vector<p6::Plane>&p){auto begin=std::chrono::steady_clock::now();auto value=p6::analyze(p,stats,mode);++api_calls;worst_api_us=std::max(worst_api_us,std::chrono::duration<double,std::micro>(std::chrono::steady_clock::now()-begin).count());return value;};
   auto result=timed(ps);json row={{"name",c.at("name")},{"kind",result.kind()},{"dimension",result.dimension},{"reason",result.reason}};
   if(c.contains("query")){
    auto query=c["query"].get<p6::Plane>();if(!p6::finite({query}))throw std::runtime_error("nonfinite query");auto back=ps;back.push_back(query);auto front=ps;front.push_back(p6::opposite(query));auto section=back;section.push_back(p6::opposite(query));
    auto f=timed(front),b=timed(back),cut=timed(section);
    row["front_dimension"]=f.dimension;row["back_dimension"]=b.dimension;row["section_dimension"]=cut.dimension;
    // Strict directional extent: feasibility of points off the plane. A child
    // with same dimension as section may still extend; enumerate child vertices.
    auto extent=[&](const std::vector<p6::Plane>&region,int desired){bool found=false;
     if(result.dimension==-2)return -1;
     p6::vertices(region,stats,mode,[&](p6::Candidate&v){if(v.side(query,v.denominator())==desired){found=true;return true;}return false;});return int(found);};
    row["strict_front"]=extent(ps,1);row["strict_back"]=extent(ps,-1);
   }
   if(c.contains("point")){
    auto point=c["point"].get<std::array<double,3>>();bool okay=true;for(auto&p:ps){auto side=p6::point_side(p,point,stats,mode);if(!side)throw std::runtime_error("unresolved point predicate");okay&=*side<=0;}row["point_consistent"]=okay;
    if(c.contains("query")){auto side=p6::point_side(c["query"].get<p6::Plane>(),point,stats,mode);row["point_query_sign"]=side?json(*side):json(nullptr);}
   }
   if(c.contains("relation"))row["relation"]=p6::relation(c["relation"][0].get<p6::Plane>(),c["relation"][1].get<p6::Plane>());
   double us=std::chrono::duration<double,std::micro>(std::chrono::steady_clock::now()-start).count();
   row["microseconds"]=us;row["region_api_calls"]=api_calls;row["worst_region_api_us"]=worst_api_us;row["worst_sign_ns"]=stats.worst_sign_ns;row["stats"]={{"fast",stats.fast},{"adaptive",stats.adaptive},{"exact",stats.exact},{"triples",stats.triples},{"exact_homogeneous_builds",stats.exact_homogeneous_builds},{"exact_rank_constraints",stats.exact_rank_constraints}};
   row["allocation_calls"]=calls-ac;row["allocated_bytes"]=total_bytes-ab;row["peak_live_increment_bytes"]=peak_bytes-lb;results.push_back(row);
  }
  std::cout<<json{{"mode",m},{"long_double_digits",std::numeric_limits<long double>::digits},{"results",results}}.dump(2)<<'\n';
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
