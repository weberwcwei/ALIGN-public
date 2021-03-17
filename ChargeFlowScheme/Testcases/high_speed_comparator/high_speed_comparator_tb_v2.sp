simulator lang=spectre
global 0

include "xyz.lib"
include "./high_speed_comparator.sp"

parameters tper=0.5n vcc=0.9 vn=vcc/2-vcc/10 vp=vcc/2+vcc/10 tstop=tper*2

I1 clk vccx vin vip von vop 0 high_speed_comparator
c0 von 0 capacitor c=10f
c1 vop 0 capacitor c=10f

V0 (vccx 0) vsource dc=vcc type=dc
V1 (clk 0) vsource type=pulse val0=0 val1=vcc period=tper rise=tper/20 fall=tper/20 width=9*tper/20
V2 (vp 0) vsource dc=0 type=pwl wave=[ 0 vn (3*tper/4) vn (3*tper/4+10p) vp (7*tper/4) vp (7*tper/4+10p) vn ]
V3 (vn 0) vsource dc=0 type=pwl wave=[ 0 vp (3*tper/4) vp (3*tper/4+10p) vn (7*tper/4) vn (7*tper/4+10p) vp ]

simulatorOptions options reltol=1e-3 vabstol=1e-6 iabstol=1e-12 temp=27 \
    tnom=27 scalem=1.0 scale=1.0 gmin=1e-12 rforce=1 maxnotes=5 maxwarns=5 \
    digits=5 cols=80 pivrel=1e-3 sensfile="../psf/sens.output" \
    checklimitdest=psf ParestMode=on ParestModel=RC ParestCapScale=1.0 \

tran tran stop=tstop errpreset=conservative btsStartTime=0.0 \
    annotate=status maxiters=5 
