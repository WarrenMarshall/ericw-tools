#include "halfspace.hpp"
#include <cassert>
#include <iostream>
int main(){
 using namespace p6;
 std::vector<Plane> box={{1,0,0,1},{-1,0,0,1},{0,1,0,1},{0,-1,0,1},{0,0,1,1},{0,0,-1,1}};
 Stats s;
 assert(analyze(box,s).dimension==3);
 for(int rounding:{FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO}){
  std::fesetround(rounding);assert(analyze(box,s).dimension==-2);
  assert(!point_side(box[0],{0,0,0},s,Mode::filtered));assert(relation(box[0],box[0])=="Unresolved");
 }
 std::fesetround(FE_TONEAREST);
#if defined(__SSE__)
 unsigned csr=_mm_getcsr();_mm_setcsr(csr|(1<<15));assert(analyze(box,s).dimension==-2);_mm_setcsr(csr);
#endif
 auto invalid=box;invalid.push_back({1,0,0,std::numeric_limits<double>::infinity()});assert(analyze(invalid,s).dimension==-2);
 invalid=box;invalid.push_back({std::numeric_limits<double>::quiet_NaN(),0,0,1});assert(analyze(invalid,s).dimension==-2);
 invalid.assign(97,box[0]);assert(analyze(invalid,s).dimension==-2);
 assert(!point_side({1,0,0,1},{std::numeric_limits<double>::infinity(),0,0},s,Mode::filtered));
 assert(point_side({1e300,1e300,0,1},{1,-1,0},s,Mode::filtered)==-1);
 double tiny=std::numeric_limits<double>::denorm_min();
 assert(point_side({tiny,0,0,0},{tiny,0,0},s,Mode::filtered)==1);
 assert(relation({1,2,3,4},{2,4,6,8})=="Equivalent");
 assert(relation({1,2,3,4},{-2,-4,-6,-8})=="Opposing");
 assert(relation({1,2,3,4},{2,4,6,std::nextafter(8.,9.)})=="Distinct");
 std::cout<<"PASS: environment guards, nonfinite/size limits, exact scalar cancellation, subnormal product and scaled plane identity\n";
}
