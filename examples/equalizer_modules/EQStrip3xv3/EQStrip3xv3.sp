

.subckt CTLE vmirror_ctle vgnd vin1_ctle vin2_ctle vout1_ctle vout2_ctle vps
    MDP00 vout2_ctle vin2_ctle n1 vgnd n nfin=12 nf=2
    MDP01 n1 vin2_ctle n2 vgnd n nfin=12 nf=2

    MDP10 vout1_ctle vin1_ctle n3 vgnd n nfin=12 nf=2
    MDP11 n3 vin1_ctle n4 vgnd n nfin=12 nf=2

    MCM00 vmirror_ctle vmirror_ctle n5 vgnd n nfin=10 nf=4
    MCM01 n5 vmirror_ctle vgnd vgnd n nfin=10 nf=4

    MCM10 n2 vmirror_ctle n6 vgnd n nfin=10 nf=4
	MCM11 n6 vmirror_ctle vgnd vgnd n nfin=10 nf=4
    MCM20 n4 vmirror_ctle n8 vgnd n nfin=10 nf=4
    MCM21 n8 vmirror_ctle vgnd vgnd n nfin=10 nf=4

	R1 vps vout2_ctle 800
    R0 vps vout1_ctle 800
    R4 n2 n4 3K
    C00 n2 n4 500f
    C01 n2 n4 500f
.ends CTLE

.subckt VGA vmirror_vga vin1 vin2 s0 s1 vout_vga1 vout_vga2 vps vgnd

	MCM00 vmirror_vga vmirror_vga n1 vgnd n nfin=12 nf=4
	MCM01 n1 vmirror_vga vgnd vgnd n nfin=12 nf=4

	MCM10 n2 vmirror_vga vgnd vgnd n nfin=12 nf=4
	MCM11 n3 vmirror_vga n2 vgnd n nfin=12 nf=4

	MSW0 vcm0 vps n3 vgnd n nfin=12 nf=4

	MDP00 vout_vga2 vin2 n4 vgnd n nfin=12 nf=4
	MDP01 n4 vin2 vcm0 vgnd n nfin=12 nf=4
	MDP10 vout_vga1 vin1 n5 vgnd n nfin=12 nf=4
	MDP11 n5 vin1 vcm0 vgnd n nfin=12 nf=4


	MCM20 n6 vmirror_vga vgnd vgnd n nfin=12 nf=4
	MCM21 n7 vmirror_vga n6 vgnd n nfin=12 nf=4

	MSW1 vcm1 s0 n7 vgnd n nfin=12 nf=4

	MDP20 vout_vga2 vin2 n8 vgnd n nfin=12 nf=4
	MDP21 n8 vin2 vcm1 vgnd n nfin=12 nf=4
	MDP30 vout_vga1 vin1 n9 vgnd n nfin=12 nf=4
	MDP31 n9 vin1 vcm1 vgnd n nfin=12 nf=4

	MCM30 n10 vmirror_vga vgnd vgnd n nfin=12 nf=4
	MCM31 n11 vmirror_vga n10 vgnd n nfin=12 nf=4

	MSW2 vcm2 s1 n11 vgnd n nfin=12 nf=4

	MDP40 vout_vga2 vin2 n12 vgnd n nfin=12 nf=4
	MDP41 n12 vin2 vcm2 vgnd n nfin=12 nf=4
	MDP50 vout_vga1 vin1 n13 vgnd n nfin=12 nf=4
	MDP51 n13 vin1 vcm2 vgnd n nfin=12 nf=4

	R5 vps vout_vga2 5000
	R6 vps vout_vga1 5000

.ends VGA

.subckt VGAWithRC vmirror_vga in1 in2 s0 s1 vout_vga1 vout_vga2 vps vgnd
	X00 vmirror_vga vin1 vin2 s0 s1 vout_vga1 vout_vga2 vps vgnd VGA
	C0 in1 n1 200f
	C1 in2 n2 200f
	C2 vin1 vin2 10f
	R0 n1 vin1 2000
	R1 n2 vin2 2000
.ends VGAWithRC

.subckt VGAWithRC2 vmirror_vga in1 in2 s0 s1 vout_vga1 vout_vga2 vps vgnd
	X00 vmirror_vga vin1 vin2 s0 s1 vout_vga1 vout_vga2 vps vgnd VGA
	C0 in1 n1 200f
	C1 in2 n2 200f
	C2 n1 vin1 20f
	C3 n1 vin2 20f
	R0 vin1 vin2 4000
.ends VGAWithRC2

.subckt Adder vbiasn vbiasp vps vgnd vin1 vin2 vout
    RB0 vbiasp vin1 20000
    RB1 vbiasn vin2 20000
    R0 vps vout 300

    M00 n1 vin1 vps vps p nfin=12 nf=1
    M01 vout vin1 n1 vps p nfin=12 nf=1

	M10 vout vin2 n2 vgnd n nfin=12 nf=2
    M11 n2 vin2 vgnd vgnd n nfin=12 nf=2
.ends Adder

.subckt AdderWithCC vbiasn vbiasp vps vgnd vin vout
	X00 vbiasn vbiasp vps vgnd vin1 vin2 vout Adder
	C0 vin vin1 600f
	C1 vin vin2 600f
.ends AdderWithCC

.subckt Adder2x vbiasn vbiasp vps vgnd vin1 vin2 vout1 vout2
	X00 vbiasn vbiasp vps vgnd vin1 vout1 AdderWithCC
	X01 vbiasn vbiasp vps vgnd vin2 vout2 AdderWithCC
.ends Adder2x

.subckt AdderWoLoad vbiasn vbiasp vps vgnd vin1 vin2 vout
    RB0 vbiasp vin1 20000
    RB1 vbiasn vin2 20000

    M00 n1 vin1 vps vps p nfin=12 nf=1
    M01 vout vin1 n1 vps p nfin=12 nf=1

	M10 vout vin2 n2 vgnd n nfin=12 nf=2
    M11 n2 vin2 vgnd vgnd n nfin=12 nf=2
.ends AdderWoLoad

.subckt AdderWithCCWL vbiasn vbiasp vps vgnd vin vout
	X00 vbiasn vbiasp vps vgnd vin1 vin2 vout AdderWoLoad
	C0 vin vin1 600f
	C1 vin vin2 600f
.ends AdderWithCCWL

.subckt Adder2xWL vbiasn vbiasp vps vgnd vin1 vin2 vout1 vout2
	X00 vbiasn vbiasp vps vgnd vin1 vout1 AdderWithCCWL
	X01 vbiasn vbiasp vps vgnd vin2 vout2 AdderWithCCWL
.ends Adder2xWL

.subckt CompVGAdder vm_vga vbn_adder vbp_adder vin1 vin2 s0 s1 vout1 vout2 vps vgnd
	X00 vm_vga vin1 vin2 s0 s1 vout_vga1 vout_vga2 vps vgnd VGAWithRC
	X01 vbn_adder vbp_adder vps vgnd vout_vga1 vout_vga2 vout1 vout2 Adder2x
.ends CompVGAdder

.subckt DiffVGAdder vm_vga vbn_adder vbp_adder vin1 vin2 s0 s1 vout1 vout2 vps vgnd
	X00 vm_vga vin1 vin2 s0 s1 vout_vga1 vout_vga2 vps vgnd VGAWithRC2
	X01 vbn_adder vbp_adder vps vgnd vout_vga1 vout_vga2 vout1 vout2 Adder2xWL
.ends DiffVGAdder

.subckt EQStrip3xv3 vm_ctle vm_vga vbn_adder vbp_adder vin1 vin2 s0 s1 vout1 vout2 vps vgnd
	X00 vm_vga vbn_adder vbp_adder vin1 vin2 s0 s1 vout1a vout2a vps vgnd CompVGAdder
	X03 vm_ctle vgnd vout1a vout2a vout1 vout2 vps CTLE
.ends EQStrip3xv3