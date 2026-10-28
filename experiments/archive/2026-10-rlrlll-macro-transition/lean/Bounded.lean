import Model

namespace Sweeper

/-- Check every position at which a step is taken. The final arrival is unrestricted:
    S5 may arrive at -3, but cannot take another step there. -/
def runB : Nat → St → Option St
  | 0, s => some s
  | k + 1, s => if -2 ≤ s.x ∧ s.x ≤ 47 then (step s).bind (runB k) else none

theorem runB_add (a b : Nat) (s : St) :
    runB (a + b) s = (runB a s).bind (runB b) := by
  induction a generalizing s with
  | zero => simp [runB]
  | succ a ih =>
    have he : a + 1 + b = (a + b) + 1 := by omega
    rw [he]
    simp only [runB]
    split
    · cases step s <;> simp_all
    · rfl

theorem runB_runN (k : Nat) (s t : St) (h : runB k s = some t) :
    runN k s = some t := by
  induction k generalizing s with
  | zero => exact h
  | succ k ih =>
    simp only [runB] at h
    split at h
    · cases hs : step s with
      | none => simp [hs] at h
      | some u => simpa [runN, hs] using ih u (by simpa [hs] using h)
    · simp at h

theorem runB_emb (pre post : List Row) (k : Nat) (s t : St)
    (h : runB k s = some t) : runB k (emb pre post s) = some (emb pre post t) := by
  induction k generalizing s with
  | zero => simp [runB] at h; subst h; rfl
  | succ k ih =>
    simp only [runB] at h
    split at h
    next hb =>
      rw [runB, if_pos (show -2 ≤ (emb pre post s).x ∧ (emb pre post s).x ≤ 47 from hb)]
      cases hs : step s with
      | none => simp [hs] at h
      | some u =>
        rw [step_emb pre post s u hs]
        exact ih u (by simpa [hs] using h)
    next => simp at h

/-- Every strict prefix arrival is in the checked interval, including time zero. -/
theorem runB_prefix (k i : Nat) (s t u : St) (hk : runB k s = some t)
    (hi : i < k) (hu : runN i s = some u) : -2 ≤ u.x ∧ u.x ≤ 47 := by
  induction i generalizing k s with
  | zero =>
    simp [runN] at hu; subst hu
    cases k with
    | zero => omega
    | succ k =>
      simp only [runB] at hk
      split at hk
      · assumption
      · simp at hk
  | succ i ih =>
    cases k with
    | zero => omega
    | succ k =>
      simp only [runB] at hk
      split at hk
      · cases hs : step s with
        | none => simp [hs] at hk
        | some v =>
          exact ih k v (by simpa [hs] using hk) (by omega) (by simpa [runN, hs] using hu)
      · simp at hk

end Sweeper
