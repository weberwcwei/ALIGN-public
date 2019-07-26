.subckt Switch_NMOS  D G S
M0 (D G S 0) NMOS_VTL w=w1 l=l1
.ends Switch_NMOS

.subckt Switch_PMOS  D G S
M0 (D G S 0) PMOS_VTL w=w1 l=l1
.ends Switch_PMOS

.subckt SCM_NMOS DA DB S
M0 (DA DA S 0) NMOS_VTL w=w l=90n
M1 (DB DA S 0) NMOS_VTL w=w l=90n
.ends SCM_NMOS

.subckt CMFB_NMOS DA DB GB S
M0 (DA DA S 0) NMOS_VTL w=w l=90n
M1 (DB GB S 0) NMOS_VTL w=w l=90n
.ends CMFB_NMOS

.subckt CMC_PMOS_S  DA DB G S
M0 (DA G S 0) PMOS_VTL w=w l=90n
M1 (DB G S 0) PMOS_VTL w=w l=90n
.ends CMC_PMOS

.subckt DP_NMOS  DA DB GA GB S
M0 (DA GA S 0) NMOS_VTL w=w l=90n
M1 (DB GB S 0) NMOS_VTL w=w l=90n
.ends DP_NMOS

.subckt CMC_PMOS DA DB SA SB G
M0 (DA G SA 0) PMOS_VTL w=w l=90n
M1 (DB G SB 0) PMOS_VTL w=w l=90n
.ends CMC_PMOS

.subckt CMC_NMOS DA DB SA SB G
M0 (DA G SA 0) NMOS_VTL w=w l=90n
M1 (DB G SB 0) NMOS_VTL w=w l=90n
.ends CMC_NMOS

.subckt Cap_b PLUS MINUS BULK
CC1 PLUS MINUS BULK cap cap=60f
.ends Cap_b

.subckt Cap PLUS MINUS
CC1 PLUS MINUS cap cap=60f
.ends Cap

.subckt DCL_NMOS D S
M0 (D D S 0) NMOS_VTL w=w l=90n
.ends DCL_NMOS

.subckt DCL_PMOS D S
M0 (D D S 0) PMOS_VTL w=w l=90n
.ends DCL_PMOS

.subckt Res PLUS MINUS
RR1 PLUS MINUS res res=10k
.ends Res

.subckt spiral_ind PLUS MINUS BULK CTAP
L0 PLUS MINUS BULK CTAP spiral_sym_ct_mu_z w=9u
.ends spiral_ind

.subckt 2_stage_inv b0_inv b0_buf B<0>
MM7 b0_buf b0_inv VSS VSS nch l=60n w=1u m=1
MM4 b0_inv B<0> VSS VSS nch l=60n w=1u m=1
MM6 b0_buf b0_inv VDD VDD pch l=60n w=1u m=1
MM5 b0_inv B<0> VDD VDD pch l=60n w=1u m=1
.ends 2_stage_inv
