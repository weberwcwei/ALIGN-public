

simulator lang=spectre
global 0
include "xyz.lib"
include "./high_speed_comparator.sp"
parameters vcm_r=0.675 wireopt=5 vdd_r=1

simulator lang=spectre
I1 clk VDD n9 n10 von vop 0 high_speed_comparator
c0 von 0 capacitor c=10f
c1 vop 0 capacitor c=10f
v4 VDD 0 vsource dc=vdd_r type=dc
//V2 vac 0 vsource dc=0 mag=50m type=sine ampl=50m freq=1G delay = 300p
//v6 n9 0 vsource type=pulse dc=0 val0=0 val1=vdd_r width=0.49n period=1n rise=0.01n fall=0.01n delay=600p
v6 n9 0 vsource dc=0.5 mag=50m type=sine ampl=50m freq=0.5G delay = 300p
v7 n10 0 vsource dc=0.5 mag=50m type=sine ampl=50m freq=0.5G delay = 0p
//v7 n10 0 vsource type=pulse dc=0 val0=0 val1=vdd_r width=0.49n period=1n rise=0.01n fall=0.01n delay=300p
v8 clk 0 vsource type=pulse dc=0 val0=0 val1=vdd_r width=0.49n period=1n rise=0.01n fall=0.01n td1=0
simulatorOptions options reltol=1e-3 vabstol=1e-6 iabstol=1e-12 temp=27 \
    tnom=27 scalem=1.0 scale=1.0 gmin=1e-12 rforce=1 maxnotes=5 maxwarns=5 \
    digits=5 cols=80 pivrel=1e-3 sensfile="../psf/sens.output" \
    checklimitdest=psf
dcOp dc write="spectre.dc" maxiters=150 maxsteps=10000 annotate=status
dcOpInfo info what=oppoint where=rawfile
ac ac start=1000 stop=100G dec=10 annotate=status
tran tran start=0 stop=15e-9 step=1e-12
modelParameter info what=models where=rawfile
element info what=inst where=rawfile
outputParameter info what=output where=rawfile
designParamVals info what=parameters where=rawfile
primitives info what=primitives where=rawfile
subckts info what=subckts where=rawfile
saveOptions options save=allpub
