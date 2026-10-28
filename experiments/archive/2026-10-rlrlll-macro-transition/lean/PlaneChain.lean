import Plane
import L4Data

/-! Multi-cycle closure, part 2: blank padding and re-windowing as plane facts. `Good ox oy g p` says the plane `p` carries the window
    `g` at (ox, oy), is blank west of the window's western context columns, and is blank in every row outside the window's rows
    for all columns up to the window's last one (columns east of it are arbitrary: the older wake). -/
namespace Sweeper


def Good (ox oy : Int) (g : List Row) (p : Int → Int → Nat) : Prop :=
  Emb ox oy g p ∧ (∀ a b, a < ox - 3 → p a b = 0) ∧
    (∀ a b, a ≤ ox + 47 → (b < oy ∨ oy + (g.length : Int) ≤ b) → p a b = 0)

theorem cell?_rows (pre g post : List Row) (x y : Int) (c : Nat)
    (h : cell? (pre ++ g ++ post) x y = some c) :
    (y < pre.length ∧ cell? pre x y = some c) ∨
    (pre.length ≤ y ∧ y < pre.length + g.length ∧ cell? g x (y - pre.length) = some c) ∨
    (pre.length + g.length ≤ y ∧ cell? post x (y - pre.length - g.length) = some c) := by
  obtain ⟨hy, hx, hlt, r, hr, hrc⟩ := cell?_inv _ x y c h
  have hlt' : y.toNat < pre.length + g.length + post.length := by simp at hlt; omega
  by_cases h1 : y.toNat < pre.length
  · left
    refine ⟨by omega, ?_⟩
    unfold cell?
    rw [if_pos ⟨hy, hx⟩]
    have : (pre ++ g ++ post)[y.toNat]? = pre[y.toNat]? := by
      rw [List.append_assoc, List.getElem?_append_left h1]
    rw [this] at hr
    simp [hr, hrc]
  · by_cases h2 : y.toNat < pre.length + g.length
    · right; left
      refine ⟨by omega, by omega, ?_⟩
      unfold cell?
      have hy' : 0 ≤ y - pre.length := by omega
      rw [if_pos ⟨hy', hx⟩]
      have e : (y - pre.length).toNat = y.toNat - pre.length := by omega
      rw [e]
      have : (pre ++ g ++ post)[y.toNat]? = g[y.toNat - pre.length]? := by
        rw [List.append_assoc, List.getElem?_append_right (by omega), List.getElem?_append_left (by omega)]
      rw [this] at hr
      simp [hr, hrc]
    · right; right
      refine ⟨by omega, ?_⟩
      unfold cell?
      have hy' : 0 ≤ y - pre.length - g.length := by omega
      rw [if_pos ⟨hy', hx⟩]
      have e : (y - pre.length - g.length).toNat = y.toNat - pre.length - g.length := by omega
      rw [e]
      have : (pre ++ g ++ post)[y.toNat]? = post[y.toNat - pre.length - g.length]? := by
        rw [List.append_assoc, List.getElem?_append_right (by omega), List.getElem?_append_right (by omega)]
      rw [this] at hr
      simp [hr, hrc]

theorem cell?_replicate_blank (a : Nat) (x y : Int) (c : Nat) (h : cell? (List.replicate a blank) x y = some c) :
    c = 0 ∧ 0 ≤ y ∧ y < a ∧ 0 ≤ x + 3 ∧ x + 3 < 51 := by
  obtain ⟨hy, hx, hlt, r, hr, hrc⟩ := cell?_inv _ x y c h
  have hlt' : y.toNat < a := by simpa using hlt
  have hr' : r = blank := by
    have h3 : (List.replicate a blank)[y.toNat]? = some blank := by simp [List.getElem?_replicate, hlt']
    rw [h3] at hr
    exact (Option.some.inj hr).symm
  subst hr'
  have h2 := (List.getElem?_eq_some_iff.mp hrc)
  have hlen : (x + 3).toNat < 51 := by simpa [blank] using h2.1
  refine ⟨?_, hy, by omega, hx, by omega⟩
  have h4 := h2.2
  simp only [blank, List.getElem_replicate] at h4
  exact h4.symm

theorem cell?_map_shiftRow (g : List Row) (x y : Int) (c : Nat) (h : cell? (g.map shiftRow) x y = some c) :
    0 ≤ x + 3 ∧ x + 3 < 51 ∧ (x < 0 → c = 0) ∧ (0 ≤ x → cell? g (x - 3) y = some c) := by
  obtain ⟨hy, hx, hlt, r, hr, hrc⟩ := cell?_inv _ x y c h
  rw [List.getElem?_map] at hr
  cases hg : g[y.toNat]? with
  | none => simp [hg] at hr
  | some r0 =>
    simp only [hg, Option.map_some, Option.some.injEq] at hr
    subst hr
    unfold shiftRow at hrc
    have hlen := (List.getElem?_eq_some_iff.mp hrc).1
    simp only [List.length_append, List.length_take, List.length_cons, List.length_nil] at hlen
    refine ⟨hx, by omega, ?_, ?_⟩
    · intro hx0
      have hi : (x + 3).toNat < 3 := by omega
      rw [List.getElem?_append_left (by simpa using hi)] at hrc
      have : ([0, 0, 0] : Row)[(x + 3).toNat]? = some 0 := by
        have : (x + 3).toNat = 0 ∨ (x + 3).toNat = 1 ∨ (x + 3).toNat = 2 := by omega
        rcases this with h | h | h <;> simp [h]
      rw [this] at hrc
      exact (Option.some.inj hrc).symm
    · intro hx0
      have hi : ¬ (x + 3).toNat < 3 := by omega
      rw [List.getElem?_append_right (by simp; omega)] at hrc
      simp only [List.length_cons, List.length_nil, List.getElem?_take] at hrc
      unfold cell?
      have hx' : 0 ≤ x - 3 + 3 := by omega
      rw [if_pos ⟨hy, hx'⟩, hg]
      have e : (x - 3 + 3).toNat = (x + 3).toNat - 3 := by omega
      rw [e]
      have : (x + 3).toNat - 3 < 48 := by omega
      simp only [Option.bind_some]
      simpa [this] using hrc

/-- One cycle, seen from the plane: the run of `T` steps from the window `I` leaves the window `F`; re-reading the plane through the
    window `I1` (three columns further west, `a` blank rows added above and `b` below) gives the invariant again. -/
theorem relink (I F I1 : St) (T a b : Nat) (hrun : runN T I = some F)
    (hlink : I1.g = List.replicate a blank ++ F.g.map shiftRow ++ List.replicate b blank)
    (hx : I1.x = 0) (hFx : F.x = -3) (hy : I1.y = F.y + a) (hh : I1.h = F.h)
    (ox oy : Int) (p : Int → Int → Nat) (hG : Good ox oy I.g p) :
    let q := runP T ⟨p, ox + I.x, oy + I.y, I.h⟩
    q.x = (ox - 3) + I1.x ∧ q.y = (oy - a) + I1.y ∧ q.h = I1.h ∧ Good (ox - 3) (oy - a) I1.g q.p := by
  obtain ⟨hE, hW, hR⟩ := hG
  obtain ⟨hqx, hqy, hqh, hEF, hout⟩ := runN_sim T I F hrun ox oy p hE
  have hlen := runN_len T I F hrun
  refine ⟨by omega, by omega, by omega, ?_, ?_, ?_⟩
  · intro x y c hc
    rw [hlink] at hc
    have key := cell?_rows (List.replicate a blank) (F.g.map shiftRow) (List.replicate b blank) x y c hc
    rcases key with ⟨h1, h2⟩ | ⟨h1, h2, h4⟩ | ⟨h1, h2⟩
    · obtain ⟨hc0, hy0, hya, hx0, hx1⟩ := cell?_replicate_blank a x y c h2
      subst hc0
      simp only [List.length_replicate] at h1
      rw [hout _ _ (cell?_none_of_row_neg _ _ _ (by omega))]
      exact hR _ _ (by omega) (Or.inl (by omega))
    · simp only [List.length_replicate] at h4
      obtain ⟨hx0, hx1, hneg, hpos⟩ := cell?_map_shiftRow _ _ _ _ h4
      simp only [List.length_replicate, List.length_map] at h1 h2
      by_cases hx2 : x < 0
      · rw [hneg hx2]
        rw [hout _ _ (cell?_none_of_col_neg _ _ _ (by omega))]
        exact hW _ _ (by omega)
      · have := hEF (x - 3) (y - a) c (hpos (by omega))
        have e1 : ox - 3 + x = ox + (x - 3) := by omega
        have e2 : oy - a + y = oy + (y - a) := by omega
        rw [e1, e2]
        exact this
    · obtain ⟨hc0, hy0, hya, hx0, hx1⟩ := cell?_replicate_blank b x _ c h2
      subst hc0
      simp only [List.length_replicate, List.length_map] at h1
      rw [hout _ _ (cell?_none_of_row_ge _ _ _ (by omega))]
      exact hR _ _ (by omega) (Or.inr (by omega))
  · intro a' b' ha
    rw [hout _ _ (cell?_none_of_col_neg _ _ _ (by omega))]
    exact hW _ _ (by omega)
  · intro a' b' ha hb
    simp only [hlink, List.length_append, List.length_replicate, List.length_map] at hb
    rcases hb with hb | hb
    · rw [hout _ _ (cell?_none_of_row_neg _ _ _ (by omega))]
      exact hR _ _ (by omega) (Or.inl (by omega))
    · rw [hout _ _ (cell?_none_of_row_ge _ _ _ (by omega))]
      exact hR _ _ (by omega) (Or.inr (by omega))

end Sweeper
