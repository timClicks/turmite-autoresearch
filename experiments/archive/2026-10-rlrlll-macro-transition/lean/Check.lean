import Model
import Iter
import Data
import L4Data
import PlaneForever
import Cycler
/-! `lake env lean Check.lean` prints the axioms every theorem used. Expected: only the core axioms (propext, Quot.sound, ...),
    no `sorryAx`, no `Lean.ofReduceBool` (that one would mean `native_decide`). -/
open Sweeper
#print axioms runN_emb
#print axioms descent_iter
#print axioms return_iter
#print axioms descent_cert0
#print axioms descent_cert1
#print axioms descent_cert2
#print axioms return_cert0
#print axioms return_cert1
#print axioms return_cert2
#print axioms descent_all0
#print axioms descent_all1
#print axioms descent_all2
#print axioms return_all0
#print axioms return_all1
#print axioms return_all2
#print axioms runB_add
#print axioms runB_runN
#print axioms runB_emb
#print axioms runB_prefix
#print axioms descent_iterB
#print axioms return_iterB
#print axioms compose_band
#print axioms cycle_chain
#print axioms s1_cert0
#print axioms s1_cert1
#print axioms s1_cert2
#print axioms s3_cert0
#print axioms s3_cert1
#print axioms s3_cert2
#print axioms s5_cert0
#print axioms s5_cert1
#print axioms s5_cert2
#print axioms descent_certB0
#print axioms descent_certB1
#print axioms descent_certB2
#print axioms return_certB0
#print axioms return_certB1
#print axioms return_certB2
#print axioms composition0
#print axioms composition1
#print axioms composition2
#print axioms cycle0
#print axioms cycle1
#print axioms cycle2
#print axioms cycle_runN0
#print axioms cycle_runN1
#print axioms cycle_runN2
#print axioms first_arrival0
#print axioms first_arrival1
#print axioms first_arrival2
#print axioms target_ant0
#print axioms target_ant1
#print axioms target_ant2
#print axioms step_sim
#print axioms runN_sim
#print axioms relink
#print axioms link0
#print axioms link1
#print axioms link2
#print axioms good_step
#print axioms forever
#print axioms good_ideal
#print axioms forever_ideal
#print axioms Sweeper.cycler
#print axioms Sweeper.rect_mid
#print axioms Sweeper.grun_agree
#print axioms Sweeper.grun_untouched
#print axioms Sweeper.gstep_shift
#print axioms Sweeper.grun_shift
