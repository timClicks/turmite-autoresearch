import Plane

/-! Soundness of the rectangle translated-cycler certificate (experiments/archive/2026-10-highway-decider), for a generic rule.

    An ant of the project's family on the infinite plane: `n` colours, turn table `turn`, the heading tables `dx`, `dy` of `Model.lean`.
    Hypotheses (a)-(d) of `cycler` are the four clauses checked by `decide.py`; the conclusion says that, for every `k`, after `k * P` steps the
    ant is at `a + k v` with the same heading and the plane restricted to the moving window `W + k v` is the initial plane shifted by `k v`. -/
namespace Sweeper

structure GRule where
  n : Nat
  turn : Nat → Nat

def gstep (R : GRule) (s : PSt) : PSt :=
  { p := fun a b => if a = s.x ∧ b = s.y then (s.p s.x s.y + 1) % R.n else s.p a b
    x := s.x + dx ((s.h + R.turn (s.p s.x s.y)) % 4)
    y := s.y + dy ((s.h + R.turn (s.p s.x s.y)) % 4)
    h := (s.h + R.turn (s.p s.x s.y)) % 4 }

def grun (R : GRule) : Nat → PSt → PSt
  | 0, s => s
  | k + 1, s => grun R k (gstep R s)

theorem grun_add (R : GRule) (a b : Nat) (s : PSt) : grun R (a + b) s = grun R b (grun R a s) := by
  induction a generalizing s with
  | zero => simp [grun]
  | succ a ih =>
    have : a + 1 + b = (a + b) + 1 := by omega
    rw [this]
    simp only [grun]
    exact ih _

def shiftP (ux uy : Int) (p : Int → Int → Nat) : Int → Int → Nat := fun a b => p (a - ux) (b - uy)

def shiftS (ux uy : Int) (s : PSt) : PSt := ⟨shiftP ux uy s.p, s.x + ux, s.y + uy, s.h⟩

theorem gstep_shift (R : GRule) (ux uy : Int) (s : PSt) : gstep R (shiftS ux uy s) = shiftS ux uy (gstep R s) := by
  obtain ⟨p, x, y, h⟩ := s
  have e1 : x + ux - ux = x := by omega
  have e2 : y + uy - uy = y := by omega
  have hp : (gstep R (shiftS ux uy ⟨p, x, y, h⟩)).p = (shiftS ux uy (gstep R ⟨p, x, y, h⟩)).p := by
    funext a b
    simp only [gstep, shiftS, shiftP, e1, e2]
    by_cases hc : a = x + ux ∧ b = y + uy
    · have hc' : a - ux = x ∧ b - uy = y := ⟨by omega, by omega⟩
      rw [if_pos hc, if_pos hc']
    · have hc' : ¬ (a - ux = x ∧ b - uy = y) := fun e => hc ⟨by omega, by omega⟩
      rw [if_neg hc, if_neg hc']
  simp only [gstep, shiftS, shiftP, e1, e2] at hp ⊢
  simp only [PSt.mk.injEq]
  exact ⟨hp, by omega, by omega, trivial⟩

theorem grun_shift (R : GRule) (ux uy : Int) : ∀ (k : Nat) (s : PSt), grun R k (shiftS ux uy s) = shiftS ux uy (grun R k s) := by
  intro k
  induction k with
  | zero => intro s; rfl
  | succ k ih => intro s; simp only [grun]; rw [gstep_shift, ih]

/-- Locality: two planes that agree on a set `S` that contains every cell the first ant stands on give the same ant and agree on `S`. -/
theorem grun_agree (R : GRule) (S : Int → Int → Prop) : ∀ (k : Nat) (s t : PSt),
    s.x = t.x → s.y = t.y → s.h = t.h → (∀ a b, S a b → s.p a b = t.p a b) →
    (∀ i, i < k → S (grun R i s).x (grun R i s).y) →
    (grun R k s).x = (grun R k t).x ∧ (grun R k s).y = (grun R k t).y ∧ (grun R k s).h = (grun R k t).h ∧
      (∀ a b, S a b → (grun R k s).p a b = (grun R k t).p a b) := by
  intro k
  induction k with
  | zero => intro s t hx hy hh hp _; exact ⟨hx, hy, hh, hp⟩
  | succ k ih =>
    intro s t hx hy hh hp hS
    have hS0 : S s.x s.y := hS 0 (by omega)
    have hpt : s.p s.x s.y = t.p s.x s.y := hp _ _ hS0
    have hpt' : s.p s.x s.y = t.p t.x t.y := by rw [hpt, ← hx, ← hy]
    simp only [grun]
    apply ih (gstep R s) (gstep R t)
    · simp only [gstep]; rw [hpt', hx, hh]
    · simp only [gstep]; rw [hpt', hy, hh]
    · simp only [gstep]; rw [hpt', hh]
    · intro a b hab
      simp only [gstep]
      by_cases hc : a = s.x ∧ b = s.y
      · have hc' : a = t.x ∧ b = t.y := ⟨by rw [hc.1, hx], by rw [hc.2, hy]⟩
        rw [if_pos hc, if_pos hc', hpt, hx, hy]
      · have hc' : ¬ (a = t.x ∧ b = t.y) := fun e => hc ⟨by rw [e.1, hx], by rw [e.2, hy]⟩
        rw [if_neg hc, if_neg hc']
        exact hp a b hab
    · intro i hi
      exact hS (i + 1) (by omega)

/-- A cell the ant never stands on keeps its colour. -/
theorem grun_untouched (R : GRule) : ∀ (k : Nat) (s : PSt) (a b : Int),
    (∀ i, i < k → ¬ ((grun R i s).x = a ∧ (grun R i s).y = b)) → (grun R k s).p a b = s.p a b := by
  intro k
  induction k with
  | zero => intro s a b _; rfl
  | succ k ih =>
    intro s a b h
    simp only [grun]
    have h0 : ¬ (s.x = a ∧ s.y = b) := h 0 (by omega)
    rw [ih (gstep R s) a b (fun i hi => h (i + 1) (by omega))]
    simp only [gstep]
    rw [if_neg (fun e => h0 ⟨e.1.symm, e.2.symm⟩)]

def inW (x0 x1 y0 y1 u w : Int) : Prop := x0 ≤ u ∧ u ≤ x1 ∧ y0 ≤ w ∧ w ≤ y1

/-- Rectangles translated along a vector: a point in the windows `j` and `m` is in every window between them. -/
theorem rect_mid (x0 x1 y0 y1 vx vy u w : Int) (j k m : Nat) (hjk : j ≤ k) (hkm : k ≤ m)
    (h1 : inW x0 x1 y0 y1 (u - j * vx) (w - j * vy)) (h2 : inW x0 x1 y0 y1 (u - m * vx) (w - m * vy)) :
    inW x0 x1 y0 y1 (u - k * vx) (w - k * vy) := by
  obtain ⟨a1, a2, a3, a4⟩ := h1
  obtain ⟨b1, b2, b3, b4⟩ := h2
  have hjk' : (j : Int) ≤ k := by exact_mod_cast hjk
  have hkm' : (k : Int) ≤ m := by exact_mod_cast hkm
  refine ⟨?_, ?_, ?_, ?_⟩
  · rcases Int.le_total 0 vx with hv | hv
    · have := Int.mul_le_mul_of_nonneg_right hkm' hv; omega
    · have := Int.mul_le_mul_of_nonpos_right hjk' hv; omega
  · rcases Int.le_total 0 vx with hv | hv
    · have := Int.mul_le_mul_of_nonneg_right hjk' hv; omega
    · have := Int.mul_le_mul_of_nonpos_right hkm' hv; omega
  · rcases Int.le_total 0 vy with hv | hv
    · have := Int.mul_le_mul_of_nonneg_right hkm' hv; omega
    · have := Int.mul_le_mul_of_nonpos_right hjk' hv; omega
  · rcases Int.le_total 0 vy with hv | hv
    · have := Int.mul_le_mul_of_nonneg_right hjk' hv; omega
    · have := Int.mul_le_mul_of_nonpos_right hkm' hv; omega

/-- The rectangle translated-cycler theorem. (a): the ant stays in `W` during `P` steps and ends at `a + v` with the same heading;
    (b): after those steps the plane equals the initial plane shifted by `v` on `W ∩ (W + v)`; (c): the leading edge of `W` is blank;
    (d): every cell outside `W` that some `W + k v`, `k >= 1`, covers is blank. Then, for every `k`, the ant is at `a + k v` with heading `h`
    after `k * P` steps and the plane is the initial one shifted by `k v` on `W + k v`; cells never covered by a `W + j v`, `j < k`, are unchanged. -/
theorem cycler (R : GRule) (P : Nat) (x0 x1 y0 y1 vx vy : Int) (p0 : Int → Int → Nat) (a b : Int) (h : Nat)
    (ha1 : ∀ i, i < P → inW x0 x1 y0 y1 (grun R i ⟨p0, a, b, h⟩).x (grun R i ⟨p0, a, b, h⟩).y)
    (ha2 : (grun R P ⟨p0, a, b, h⟩).x = a + vx ∧ (grun R P ⟨p0, a, b, h⟩).y = b + vy ∧ (grun R P ⟨p0, a, b, h⟩).h = h)
    (hb : ∀ u w, inW x0 x1 y0 y1 u w → inW x0 x1 y0 y1 (u - vx) (w - vy) →
        (grun R P ⟨p0, a, b, h⟩).p u w = p0 (u - vx) (w - vy))
    (hc : ∀ u w, inW x0 x1 y0 y1 u w → ¬ inW x0 x1 y0 y1 (u + vx) (w + vy) → p0 u w = 0)
    (hd : ∀ u w, ¬ inW x0 x1 y0 y1 u w → (∃ k : Nat, 1 ≤ k ∧ inW x0 x1 y0 y1 (u - k * vx) (w - k * vy)) → p0 u w = 0) :
    ∀ k : Nat,
      (grun R (k * P) ⟨p0, a, b, h⟩).x = a + k * vx ∧ (grun R (k * P) ⟨p0, a, b, h⟩).y = b + k * vy ∧
      (grun R (k * P) ⟨p0, a, b, h⟩).h = h ∧
      (∀ u w, inW x0 x1 y0 y1 (u - k * vx) (w - k * vy) →
        (grun R (k * P) ⟨p0, a, b, h⟩).p u w = p0 (u - k * vx) (w - k * vy)) ∧
      (∀ u w, (∀ j : Nat, j < k → ¬ inW x0 x1 y0 y1 (u - j * vx) (w - j * vy)) →
        (grun R (k * P) ⟨p0, a, b, h⟩).p u w = p0 u w) := by
  intro k
  induction k with
  | zero =>
    refine ⟨by simp [grun], by simp [grun], by simp [grun], ?_, ?_⟩
    · intro u w _; simp [grun]
    · intro u w _; simp [grun]
  | succ k ih =>
    obtain ⟨hx, hy, hh, F1, F2⟩ := ih
    have hk1x : ((k + 1 : Nat) : Int) * vx = k * vx + vx := by push_cast; rw [Int.add_mul, Int.one_mul]
    have hk1y : ((k + 1 : Nat) : Int) * vy = k * vy + vy := by push_cast; rw [Int.add_mul, Int.one_mul]
    have e : (k + 1) * P = k * P + P := by rw [Nat.succ_mul]
    rw [e, grun_add]
    generalize hQ : grun R (k * P) ⟨p0, a, b, h⟩ = Q at hx hy hh F1 F2 ⊢
    -- the shifted copy of the start, and the set S = W + k v
    have hT := grun_shift R (k * vx) (k * vy) P ⟨p0, a, b, h⟩
    have hTi : ∀ i, grun R i (shiftS (k * vx) (k * vy) ⟨p0, a, b, h⟩) = shiftS (k * vx) (k * vy) (grun R i ⟨p0, a, b, h⟩) :=
      fun i => grun_shift R (k * vx) (k * vy) i ⟨p0, a, b, h⟩
    have hstandT : ∀ i, i < P → inW x0 x1 y0 y1 ((grun R i (shiftS (k * vx) (k * vy) ⟨p0, a, b, h⟩)).x - k * vx)
        ((grun R i (shiftS (k * vx) (k * vy) ⟨p0, a, b, h⟩)).y - k * vy) := by
      intro i hi
      have := ha1 i hi
      rw [hTi i]
      simp only [shiftS]
      have e1 : (grun R i ⟨p0, a, b, h⟩).x + k * vx - k * vx = (grun R i ⟨p0, a, b, h⟩).x := by omega
      have e2 : (grun R i ⟨p0, a, b, h⟩).y + k * vy - k * vy = (grun R i ⟨p0, a, b, h⟩).y := by omega
      rw [e1, e2]
      exact this
    have hag : ∀ u w, inW x0 x1 y0 y1 (u - k * vx) (w - k * vy) →
        (shiftS (k * vx) (k * vy) ⟨p0, a, b, h⟩).p u w = Q.p u w := by
      intro u w hS
      exact (F1 u w hS).symm
    have hagree := fun i (hiP : i ≤ P) => grun_agree R (fun u w => inW x0 x1 y0 y1 (u - k * vx) (w - k * vy)) i
      (shiftS (k * vx) (k * vy) ⟨p0, a, b, h⟩) Q (by simp only [shiftS]; omega) (by simp only [shiftS]; omega)
      (by simp only [shiftS]; exact hh.symm) hag
      (fun i' hi' => hstandT i' (by omega))
    obtain ⟨hax, hay, hah, hap⟩ := hagree P (Nat.le_refl P)
    rw [hTi P] at hax hay hah hap
    simp only [shiftS, shiftP] at hax hay hah hap
    obtain ⟨h2x, h2y, h2h⟩ := ha2
    have hun : ∀ u w, ¬ inW x0 x1 y0 y1 (u - k * vx) (w - k * vy) → (grun R P Q).p u w = Q.p u w := by
      intro u w hnS
      apply grun_untouched
      intro i hi he
      obtain ⟨gx, gy, _, _⟩ := hagree i (Nat.le_of_lt hi)
      have := hstandT i hi
      rw [gx, gy, he.1, he.2] at this
      exact hnS this
    refine ⟨by omega, by omega, by omega, ?_, ?_⟩
    · intro u w hw
      have hw0 := hw
      rw [hk1x, hk1y] at hw ⊢
      obtain ⟨c1, c2, c3, c4⟩ := hw
      by_cases hS : inW x0 x1 y0 y1 (u - k * vx) (w - k * vy)
      · have h1 := hap u w hS
        rw [← h1] at *
        rw [hb (u - k * vx) (w - k * vy) hS ⟨by omega, by omega, by omega, by omega⟩]
        have e3 : u - k * vx - vx = u - (k * vx + vx) := by omega
        have e4 : w - k * vy - vy = w - (k * vy + vy) := by omega
        rw [e3, e4]
      · have hnu := hun u w hS
        have hz0 : p0 u w = 0 := by
          apply hd u w
          · intro hin
            apply hS
            exact rect_mid x0 x1 y0 y1 vx vy u w 0 k (k + 1) (Nat.zero_le k) (Nat.le_succ k) (by simpa using hin) hw0
          · exact ⟨k + 1, by omega, hw0⟩
        have hz1 : p0 (u - (k * vx + vx)) (w - (k * vy + vy)) = 0 := by
          apply hc _ _ ⟨c1, c2, c3, c4⟩
          have e5 : u - (k * vx + vx) + vx = u - k * vx := by omega
          have e6 : w - (k * vy + vy) + vy = w - k * vy := by omega
          rw [e5, e6]
          exact hS
        rw [hnu, F2 u w ?_, hz0, hz1]
        intro j hj hjin
        exact hS (rect_mid x0 x1 y0 y1 vx vy u w j k (k + 1) (Nat.le_of_lt hj) (Nat.le_succ k) hjin hw0)
    · intro u w hj
      have hnS : ¬ inW x0 x1 y0 y1 (u - k * vx) (w - k * vy) := hj k (Nat.lt_succ_self k)
      rw [hun u w hnS]
      exact F2 u w (fun j hj' => hj j (by omega))

end Sweeper
