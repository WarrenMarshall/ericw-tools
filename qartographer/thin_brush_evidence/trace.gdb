set pagination off
set print pretty off
set breakpoint pending on
break /home/warrenmarshall/dev/ericw-tools/qbsp/brushbsp.cc:664
commands
silent
printf "VOLUME_TEST n=(%g,%g,%g) dist=%.12g front=%.12g back=%.12g\n",split.normal.v._M_elems[0],split.normal.v._M_elems[1],split.normal.v._M_elems[2],split.dist,d_front,d_back
continue
end
run -bsp2 -notex -nopercent /tmp/qqbsp-p3/boundary/p1/thin-default/thin.map
