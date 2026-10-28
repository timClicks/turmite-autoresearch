import Bounded
/-! Bounded counterparts of Iter.lean, preserving the original L1-L3 proofs.
    The bounded finite certificates are discharged in L4Data.lean. -/
namespace Sweeper

/-- Descent: `A . bulk bulk` (ant on the first bulk row) runs to `rp . A` in 20 steps, ant on the row below.
    Then for every n, `pre . A . bulk^(2n) . post` runs to `pre . rp^n . A . post` in 20 n steps. -/
theorem descent_iterB (A bulk : Row) (rp : List Row) (x : Int) (h : Nat) (hrp : rp.length = 2)
    (cert : runB 20 { g := [A, bulk, bulk], x := x, y := 1, h := h } = some { g := rp ++ [A], x := x, y := 3, h := h }) :
    ∀ (n : Nat) (pre post : List Row),
      runB (20 * n) { g := pre ++ [A] ++ List.replicate (2 * n) bulk ++ post, x := x, y := pre.length + 1, h := h }
        = some { g := pre ++ (List.replicate n rp).flatten ++ [A] ++ post, x := x,
                 y := pre.length + 1 + 2 * (n : Int), h := h } := by
  intro n
  induction n with
  | zero =>
    intro pre post
    simp [runB]
  | succ n ih =>
    intro pre post
    have e20 : 20 * (n + 1) = 20 + 20 * n := by omega
    have e2 : 2 * (n + 1) = 2 * n + 1 + 1 := by omega
    rw [e20, runB_add]
    have hfirst := runB_emb pre (List.replicate (2 * n) bulk ++ post) 20 _ _ cert
    have hs : ({ g := pre ++ [A] ++ List.replicate (2 * (n + 1)) bulk ++ post, x := x, y := pre.length + 1, h := h } : St)
        = emb pre (List.replicate (2 * n) bulk ++ post) { g := [A, bulk, bulk], x := x, y := 1, h := h } := by
      simp only [emb, e2, List.replicate_succ, List.cons_append, List.append_assoc, List.nil_append,
        St.mk.injEq, true_and, and_true]
      omega
    rw [hs, hfirst, Option.bind_some]
    have hs2 : emb pre (List.replicate (2 * n) bulk ++ post) { g := rp ++ [A], x := x, y := 3, h := h }
        = { g := (pre ++ rp) ++ [A] ++ List.replicate (2 * n) bulk ++ post, x := x, y := (pre ++ rp).length + 1, h := h } := by
      simp only [emb, List.length_append, hrp, List.append_assoc, St.mk.injEq]
      exact ⟨trivial, trivial, by omega, trivial⟩
    rw [hs2, ih (pre ++ rp) post]
    simp only [List.length_append, hrp, List.replicate_succ, List.flatten_cons, List.append_assoc, Option.some.injEq,
      St.mk.injEq, true_and, and_true]
    omega

theorem flatten_replicate_lengthB (r : List Row) (hr : r.length = 2) (n : Nat) :
    ((List.replicate n r).flatten).length = 2 * n := by
  induction n with
  | zero => simp
  | succ n ih => simp only [List.replicate_succ, List.flatten_cons, List.length_append, hr, ih]; omega

/-- Return (the mirror image): `rp . Ap` with the ant on the last row of `rp` runs in 4 steps to `Ap . rpp`, ant on the row
    above. Then for every n, `pre . rp^n . Ap . post` (ant on the last `rp` row) runs to `pre . Ap . rpp^n . post` in 4 n steps. -/
theorem return_iterB (Ap : Row) (rp rpp : List Row) (x : Int) (h : Nat) (hrp : rp.length = 2)
    (cert : runB 4 { g := rp ++ [Ap], x := x, y := 1, h := h } = some { g := [Ap] ++ rpp, x := x, y := -1, h := h }) :
    ∀ (n : Nat) (pre post : List Row),
      runB (4 * n) { g := pre ++ (List.replicate n rp).flatten ++ [Ap] ++ post, x := x,
                     y := pre.length + 2 * (n : Int) - 1, h := h }
        = some { g := pre ++ [Ap] ++ (List.replicate n rpp).flatten ++ post, x := x, y := pre.length - 1, h := h } := by
  intro n
  induction n with
  | zero =>
    intro pre post
    simp [runB]
  | succ n ih =>
    intro pre post
    have e4 : 4 * (n + 1) = 4 + 4 * n := by omega
    rw [e4, runB_add]
    have hF := flatten_replicate_lengthB rp hrp n
    have hfirst := runB_emb (pre ++ (List.replicate n rp).flatten) post 4 _ _ cert
    have hs : ({ g := pre ++ (List.replicate (n + 1) rp).flatten ++ [Ap] ++ post, x := x,
                 y := pre.length + 2 * ((n + 1 : Nat) : Int) - 1, h := h } : St)
        = emb (pre ++ (List.replicate n rp).flatten) post { g := rp ++ [Ap], x := x, y := 1, h := h } := by
      simp only [emb, List.replicate_succ', List.flatten_append, List.flatten_singleton, List.append_assoc,
        List.length_append, hF, St.mk.injEq]
      exact ⟨trivial, trivial, by omega, trivial⟩
    rw [hs, hfirst, Option.bind_some]
    have hs2 : emb (pre ++ (List.replicate n rp).flatten) post { g := [Ap] ++ rpp, x := x, y := -1, h := h }
        = { g := pre ++ (List.replicate n rp).flatten ++ [Ap] ++ (rpp ++ post), x := x,
            y := pre.length + 2 * (n : Int) - 1, h := h } := by
      simp only [emb, List.length_append, hF, List.append_assoc, List.singleton_append, List.cons_append,
        St.mk.injEq]
      exact ⟨trivial, trivial, by omega, trivial⟩
    rw [hs2, ih pre (rpp ++ post)]
    simp only [List.replicate_succ', List.flatten_append, List.flatten_singleton, List.append_assoc, Option.some.injEq,
      St.mk.injEq, true_and, and_true]

end Sweeper

