import IterB
import Composition

-- Symbolic chaining must not expand the finite step interpreter.
attribute [local irreducible] Sweeper.runB
namespace Sweeper

theorem runB_seq (a b : Nat) (s t u : St)
    (ha : runB a s = some t) (hb : runB b t = some u) :
    runB (a+b) s = some u := by rw [runB_add, ha]; exact hb

/-- One cycle, assembled entirely from bounded patch runs. Padding is an input
    owned by this cycle; this theorem does not replenish it for the next cycle. -/
theorem cycle_chain (P Q U D E : List Row) (bulk A Ap : Row) (rp rpp : List Row)
    (y z : Int) (s1 s5 : Nat) (hrp : rp.length = 2)
    (c1 : runB s1 {g := P ++ [bulk], x := 0, y := y, h := 3} =
      some {g := U ++ [A], x := -1, y := U.length + 1, h := 2})
    (cd : runB 20 {g := [A, bulk, bulk], x := -1, y := 1, h := 2} =
      some {g := rp ++ [A], x := -1, y := 3, h := 2})
    (c3 : runB 216 {g := [A, bulk] ++ Q, x := -1, y := 1, h := 2} =
      some {g := [Ap] ++ D, x := 1, y := -1, h := 0})
    (cr : runB 4 {g := rp ++ [Ap], x := 1, y := 1, h := 0} =
      some {g := [Ap] ++ rpp, x := 1, y := -1, h := 0})
    (c5 : runB s5 {g := U ++ [Ap], x := 1, y := U.length - 1, h := 0} =
      some {g := E, x := -3, y := z, h := 3}) (n : Nat) :
    runB (s1 + 20*n + 216 + 4*n + s5)
      {g := P ++ List.replicate (2+2*n) bulk ++ Q, x := 0, y := y, h := 3} =
      some {g := E ++ (List.replicate n rpp).flatten ++ D, x := -3, y := z, h := 3} := by
  have h1 := runB_emb [] (List.replicate (2*n) bulk ++ [bulk] ++ Q) s1 _ _ c1
  have h1' : runB s1 {g := P ++ List.replicate (2+2*n) bulk ++ Q, x := 0, y := y, h := 3} =
      some {g := U ++ [A] ++ List.replicate (2*n) bulk ++ [bulk] ++ Q,
            x := -1, y := U.length + 1, h := 2} := by
    have he : List.replicate (2+2*n) bulk = [bulk] ++ List.replicate (2*n) bulk ++ [bulk] := by
      rw [show 2+2*n = 1+2*n+1 by omega, replicate_sum, replicate_sum]
      rfl
    simpa only [emb, List.nil_append, List.append_nil, List.length_nil, Int.natCast_zero,
      Int.add_zero, he, List.append_assoc] using h1
  have hd := descent_iterB A bulk rp (-1) 2 hrp cd n U ([bulk] ++ Q)
  have h3 := runB_emb (U ++ (List.replicate n rp).flatten) [] 216 _ _ c3
  have h3' : runB 216
      {g := U ++ (List.replicate n rp).flatten ++ [A] ++ [bulk] ++ Q,
       x := -1, y := U.length + 1 + 2*(n : Int), h := 2} =
      some {g := U ++ (List.replicate n rp).flatten ++ [Ap] ++ D,
            x := 1, y := U.length + 2*(n : Int) - 1, h := 0} := by
    simpa [emb, List.append_assoc, List.length_append, flatten_replicate_lengthB rp hrp n,
      Int.sub_eq_add_neg, Int.add_comm, Int.add_left_comm, Int.add_assoc] using h3
  have hr := return_iterB Ap rp rpp 1 0 hrp cr n U D
  have h5 := runB_emb [] ((List.replicate n rpp).flatten ++ D) s5 _ _ c5
  have h5' : runB s5
      {g := U ++ [Ap] ++ (List.replicate n rpp).flatten ++ D,
       x := 1, y := U.length - 1, h := 0} =
      some {g := E ++ (List.replicate n rpp).flatten ++ D, x := -3, y := z, h := 3} := by
    simpa [emb, List.append_assoc] using h5
  simp only [List.append_assoc] at h1' hd h3' hr h5' ⊢
  exact runB_seq _ _ _ _ _
    (runB_seq _ _ _ _ _ (runB_seq _ _ _ _ _ (runB_seq _ _ _ _ _ h1' hd) h3') hr) h5'

end Sweeper



