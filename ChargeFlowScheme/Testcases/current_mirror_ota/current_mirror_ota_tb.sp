//
//
simulator lang=spectre
global VDD 0
include "xyz.lib"
include "./current_mirror_ota.sp"
parameters vcm_r=0.7 wireopt=5 vdd_r=0.8

simulator lang=spectre
//.subckt current_mirror_ota id vinn vinp vss vdd voutp vbiasnd
I1 net17 n9 n10 0 VDD voutp current_mirror_ota
I0 VDD net17 isource dc=200e-6 type=dc
v4 VDD 0 vsource dc=vdd_r type=dc
V2 vac 0 vsource dc=0 mag=50m type=sine ampl=50m freq=1G
E1 n9 vcm vac 0 vcvs gain=1.0
E0 n10 vcm vac 0 vcvs gain=-1.0
V1 vcm 0 vsource dc=vcm_r mag=0 type=dc
C0 voutp 0 capacitor c=100.0f
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
