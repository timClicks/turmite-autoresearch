import Model

/-! Multi-cycle closure, part 1: an infinite-plane model of the same ant and a simulation lemma.

    `PSt` is the ant on all of Z x Z: colours are a function `Int -> Int -> Nat` (no window, no failure). `Emb ox oy g p` says that the
    window `g` (rows of the list model; list column index x + 3, list row index y) sits in the plane with its origin at (ox, oy) and the
    plane agrees with it on every window cell. A successful run of the *window* model is then a run of the plane, the plane agrees with
    the window's end state, and the plane is unchanged on every cell outside the window. -/
namespace Sweeper

structure PSt where
  p : Int → Int → Nat
  x : Int
  y : Int
  h : Nat

def stepP (s : PSt) : PSt :=
  { p := fun a b => if a = s.x ∧ b = s.y then (s.p s.x s.y + 1) % 6 else s.p a b
    x := s.x + dx ((s.h + turn (s.p s.x s.y)) % 4)
    y := s.y + dy ((s.h + turn (s.p s.x s.y)) % 4)
    h := (s.h + turn (s.p s.x s.y)) % 4 }

def runP : Nat → PSt → PSt
  | 0, s => s
  | k + 1, s => runP k (stepP s)

theorem runP_add (a b : Nat) (s : PSt) : runP (a + b) s = runP b (runP a s) := by
  induction a generalizing s with
  | zero => simp [runP]
  | succ a ih =>
    have : a + 1 + b = (a + b) + 1 := by omega
    rw [this]
    simp only [runP]
    exact ih _

/-- The plane agrees with the window `g` placed at origin (ox, oy). -/
def Emb (ox oy : Int) (g : List Row) (p : Int → Int → Nat) : Prop :=
  ∀ x y c, cell? g x y = some c → p (ox + x) (oy + y) = c

theorem cell?_none_of_row_neg (g : List Row) (x y : Int) (h : y < 0) : cell? g x y = none := by
  unfold cell?
  rw [if_neg (by omega)]

theorem cell?_none_of_col_neg (g : List Row) (x y : Int) (h : x + 3 < 0) : cell? g x y = none := by
  unfold cell?
  rw [if_neg (by omega)]

theorem cell?_none_of_row_ge (g : List Row) (x y : Int) (h : g.length ≤ y.toNat) : cell? g x y = none := by
  unfold cell?
  split
  · rw [List.getElem?_eq_none h]
    rfl
  · rfl

theorem cell?_setCell (g : List Row) (x y : Int) (c0 c : Nat) (h : cell? g x y = some c0) (u v : Int) :
    cell? (setCell g x y c) u v = if u = x ∧ v = y then some c else cell? g u v := by
  obtain ⟨hy, hx, hlt, r, hr, hrc⟩ := cell?_inv g x y c0 h
  have hg : g.getD y.toNat [] = r := by
    simp [List.getD_eq_getElem?_getD, hr]
  have hxlt : (x + 3).toNat < r.length := (List.getElem?_eq_some_iff.mp hrc).1
  unfold setCell
  rw [hg]
  by_cases hv : 0 ≤ v ∧ 0 ≤ u + 3
  · have hu0 : (u + 3).toNat = (x + 3).toNat ↔ u = x := by omega
    have hv0 : v.toNat = y.toNat ↔ v = y := by omega
    by_cases huv : u = x ∧ v = y
    · obtain ⟨rfl, rfl⟩ := huv
      rw [if_pos ⟨rfl, rfl⟩]
      unfold cell?
      rw [if_pos hv]
      simp [List.getElem?_set, hlt, hxlt]
    · rw [if_neg huv]
      unfold cell?
      rw [if_pos hv, if_pos hv]
      by_cases hvy : v.toNat = y.toNat
      · have huu : ¬ (x + 3).toNat = (u + 3).toNat := fun e => huv ⟨hu0.mp e.symm, hv0.mp hvy⟩
        rw [hvy]
        have hgs : g[y.toNat]'hlt = r := by
          have := List.getElem?_eq_getElem hlt
          rw [hr] at this
          exact (Option.some.inj this).symm
        simp [List.getElem?_set, hlt, huu, hr, hgs]
      · have hvy' : ¬ y.toNat = v.toNat := fun e => hvy e.symm
        simp [List.getElem?_set, hvy']
  · rw [if_neg (by omega : ¬ (u = x ∧ v = y))]
    unfold cell?
    rw [if_neg hv, if_neg hv]

theorem step_sim (s s' : St) (h : step s = some s') (ox oy : Int) (p : Int → Int → Nat)
    (hE : Emb ox oy s.g p) :
    let q := stepP ⟨p, ox + s.x, oy + s.y, s.h⟩
    q.x = ox + s'.x ∧ q.y = oy + s'.y ∧ q.h = s'.h ∧ Emb ox oy s'.g q.p ∧
      (∀ a b, ¬ (a = ox + s.x ∧ b = oy + s.y) → q.p a b = p a b) := by
  unfold step at h
  cases hc : cell? s.g s.x s.y with
  | none => simp [hc] at h
  | some c =>
    simp only [hc, Option.some.injEq] at h
    subst h
    have hp : p (ox + s.x) (oy + s.y) = c := hE _ _ _ hc
    simp only [stepP, hp]
    refine ⟨by omega, by omega, trivial, ?_, ?_⟩
    · intro u v d hd
      rw [cell?_setCell s.g s.x s.y c ((c + 1) % 6) hc] at hd
      dsimp only
      by_cases huv : u = s.x ∧ v = s.y
      · rw [if_pos huv] at hd
        obtain ⟨rfl, rfl⟩ := huv
        rw [if_pos ⟨rfl, rfl⟩]
        exact Option.some.inj hd
      · rw [if_neg huv] at hd
        have : ¬ (ox + u = ox + s.x ∧ oy + v = oy + s.y) := fun e => huv ⟨by omega, by omega⟩
        rw [if_neg this]
        exact hE _ _ _ hd
    · intro a b hab
      rw [if_neg hab]

theorem step_dom (s s' : St) (h : step s = some s') (u v : Int) :
    cell? s'.g u v = none ↔ cell? s.g u v = none := by
  unfold step at h
  cases hc : cell? s.g s.x s.y with
  | none => simp [hc] at h
  | some c =>
    simp only [hc, Option.some.injEq] at h
    subst h
    simp only []
    rw [cell?_setCell s.g s.x s.y c ((c + 1) % 6) hc]
    by_cases huv : u = s.x ∧ v = s.y
    · rw [if_pos huv]
      obtain ⟨rfl, rfl⟩ := huv
      simp [hc]
    · rw [if_neg huv]

theorem runN_sim (k : Nat) (s s' : St) (h : runN k s = some s') (ox oy : Int) (p : Int → Int → Nat)
    (hE : Emb ox oy s.g p) :
    let q := runP k ⟨p, ox + s.x, oy + s.y, s.h⟩
    q.x = ox + s'.x ∧ q.y = oy + s'.y ∧ q.h = s'.h ∧ Emb ox oy s'.g q.p ∧
      (∀ a b, cell? s.g (a - ox) (b - oy) = none → q.p a b = p a b) := by
  induction k generalizing s p with
  | zero =>
    simp only [runN, Option.some.injEq] at h
    subst h
    exact ⟨rfl, rfl, rfl, hE, fun _ _ _ => rfl⟩
  | succ k ih =>
    simp only [runN] at h
    cases hs : step s with
    | none => simp [hs] at h
    | some s1 =>
      simp only [hs, Option.bind_some] at h
      obtain ⟨hx, hy, hh, hE1, hout⟩ := step_sim s s1 hs ox oy p hE
      have e : stepP ⟨p, ox + s.x, oy + s.y, s.h⟩ =
          ⟨(stepP ⟨p, ox + s.x, oy + s.y, s.h⟩).p, ox + s1.x, oy + s1.y, s1.h⟩ := by
        rw [← hx, ← hy, ← hh]
      have ih' := ih s1 h (stepP ⟨p, ox + s.x, oy + s.y, s.h⟩).p hE1
      simp only [runP]
      rw [e]
      obtain ⟨ix, iy, ih3, iE, iout⟩ := ih'
      refine ⟨ix, iy, ih3, iE, ?_⟩
      intro a b hab
      have hab1 : cell? s1.g (a - ox) (b - oy) = none := (step_dom s s1 hs _ _).mpr hab
      have h1 := iout a b hab1
      rw [h1]
      apply hout
      intro hc
      obtain ⟨c, hc'⟩ : ∃ c, cell? s.g s.x s.y = some c := by
        unfold step at hs
        cases hq : cell? s.g s.x s.y with
        | none => simp [hq] at hs
        | some c => exact ⟨c, rfl⟩
      have : a - ox = s.x ∧ b - oy = s.y := ⟨by omega, by omega⟩
      rw [this.1, this.2, hc'] at hab
      simp at hab

theorem step_len (s s' : St) (h : step s = some s') : s'.g.length = s.g.length := by
  unfold step at h
  cases hc : cell? s.g s.x s.y with
  | none => simp [hc] at h
  | some c =>
    simp only [hc, Option.some.injEq] at h
    subst h
    simp [setCell]

theorem runN_len (k : Nat) (s s' : St) (h : runN k s = some s') : s'.g.length = s.g.length := by
  induction k generalizing s with
  | zero => simp only [runN, Option.some.injEq] at h; subst h; rfl
  | succ k ih =>
    simp only [runN] at h
    cases hs : step s with
    | none => simp [hs] at h
    | some s1 =>
      simp only [hs, Option.bind_some] at h
      rw [ih s1 h, step_len s s1 hs]

end Sweeper
