import PlaneChain
import L4Data

/-! Multi-cycle closure, part 3: the three phase instances of `relink` and the induction over any number of cycles. -/
namespace Sweeper

theorem nt0 : nextTop0 = top1 := by decide +kernel
theorem nb0 : nextBottom0 = bottom1 := by decide +kernel
theorem nt1 : nextTop1 = top2 := by decide +kernel
theorem nb1 : nextBottom1 = bottom2 := by decide +kernel
theorem nt2 : nextTop2 = top0 := by decide +kernel
theorem nb2 : nextBottom2 = bottom0 := by decide +kernel

theorem pad_pad (a b : Nat) (X : List Row) :
    List.replicate a blank ++ (List.replicate b blank ++ X) = List.replicate (a + b) blank ++ X := by
  rw [← List.append_assoc, ← replicate_sum]

theorem pad_pad2 (a b : Nat) :
    List.replicate a blank ++ List.replicate b blank = List.replicate (a + b) blank := (replicate_sum a b blank).symm

theorem link0 (n : Nat) : (initial1 (n+1)).g = List.replicate 2 blank ++ (final0 n).g.map shiftRow ++ List.replicate 1 blank := by
  rw [composition0, nt0, nb0]
  simp only [initial1, show 2 + 2*(n+1) = 2*n+4 by omega, List.append_assoc, pad_pad, pad_pad2, Nat.reduceAdd]

theorem link1 (n : Nat) : (initial2 (n+1)).g = List.replicate 0 blank ++ (final1 n).g.map shiftRow ++ List.replicate 1 blank := by
  rw [composition1, nt1, nb1]
  simp only [initial2, show 2 + 2*(n+1) = 2*n+4 by omega, List.append_assoc, pad_pad, pad_pad2, Nat.reduceAdd,
    List.replicate_zero, List.nil_append]

theorem link2 (n : Nat) : (initial0 (n+1)).g = List.replicate 1 blank ++ (final2 n).g.map shiftRow ++ List.replicate 1 blank := by
  rw [composition2, nt2, nb2]
  simp only [initial0, show 2 + 2*(n+1) = 2*n+4 by omega, List.append_assoc, pad_pad, pad_pad2, Nat.reduceAdd]

theorem good_step0 (n : Nat) (ox oy : Int) (p : Int → Int → Nat) (hG : Good ox oy (initial0 n).g p) :
    let r := runP (12*(2+2*n) + 934) ⟨p, ox + (initial0 n).x, oy + (initial0 n).y, (initial0 n).h⟩
    r.x = (ox - 3) + (initial1 (n+1)).x ∧ r.y = (oy - ((2:Nat):Int)) + (initial1 (n+1)).y ∧
      r.h = (initial1 (n+1)).h ∧ Good (ox - 3) (oy - ((2:Nat):Int)) (initial1 (n+1)).g r.p :=
  relink (initial0 n) (final0 n) (initial1 (n+1)) _ 2 1 (cycle_runN0 n) (link0 n) rfl rfl rfl rfl ox oy p hG

theorem good_step1 (n : Nat) (ox oy : Int) (p : Int → Int → Nat) (hG : Good ox oy (initial1 n).g p) :
    let r := runP (12*(2+2*n) + 1058) ⟨p, ox + (initial1 n).x, oy + (initial1 n).y, (initial1 n).h⟩
    r.x = (ox - 3) + (initial2 (n+1)).x ∧ r.y = (oy - ((0:Nat):Int)) + (initial2 (n+1)).y ∧
      r.h = (initial2 (n+1)).h ∧ Good (ox - 3) (oy - ((0:Nat):Int)) (initial2 (n+1)).g r.p :=
  relink (initial1 n) (final1 n) (initial2 (n+1)) _ 0 1 (cycle_runN1 n) (link1 n) rfl rfl rfl rfl ox oy p hG

theorem good_step2 (n : Nat) (ox oy : Int) (p : Int → Int → Nat) (hG : Good ox oy (initial2 n).g p) :
    let r := runP (12*(2+2*n) + 898) ⟨p, ox + (initial2 n).x, oy + (initial2 n).y, (initial2 n).h⟩
    r.x = (ox - 3) + (initial0 (n+1)).x ∧ r.y = (oy - ((1:Nat):Int)) + (initial0 (n+1)).y ∧
      r.h = (initial0 (n+1)).h ∧ Good (ox - 3) (oy - ((1:Nat):Int)) (initial0 (n+1)).g r.p :=
  relink (initial2 n) (final2 n) (initial0 (n+1)) _ 1 1 (cycle_runN2 n) (link2 n) rfl rfl rfl rfl ox oy p hG

/-- The window of phase `q` (0, 1, 2) and height index `n` (bulk height m = 2 + 2n). -/
def initQ : Nat → Nat → St
  | 0, n => initial0 n
  | 1, n => initial1 n
  | _, n => initial2 n

def clockQ : Nat → Nat → Nat
  | 0, n => 12*(2+2*n) + 934
  | 1, n => 12*(2+2*n) + 1058
  | _, n => 12*(2+2*n) + 898

/-- Blank rows the next window adds above (the rectangle's top moves up by 2, 0, 1 rows). -/
def rowsQ : Nat → Nat
  | 0 => 2
  | 1 => 0
  | _ => 1

theorem good_step (q n : Nat) (hq : q < 3) (ox oy : Int) (p : Int → Int → Nat)
    (hG : Good ox oy (initQ q n).g p) :
    let r := runP (clockQ q n) ⟨p, ox + (initQ q n).x, oy + (initQ q n).y, (initQ q n).h⟩
    r.x = (ox - 3) + (initQ ((q+1)%3) (n+1)).x ∧ r.y = (oy - (rowsQ q : Int)) + (initQ ((q+1)%3) (n+1)).y ∧
      r.h = (initQ ((q+1)%3) (n+1)).h ∧ Good (ox - 3) (oy - (rowsQ q : Int)) (initQ ((q+1)%3) (n+1)).g r.p := by
  obtain rfl | rfl | rfl : q = 0 ∨ q = 1 ∨ q = 2 := by omega
  · exact good_step0 n ox oy p hG
  · exact good_step1 n ox oy p hG
  · exact good_step2 n ox oy p hG

def tsum : Nat → Nat → Nat → Nat
  | _, _, 0 => 0
  | q, n, N+1 => clockQ q n + tsum ((q+1)%3) (n+1) N

def asum : Nat → Nat → Nat
  | _, 0 => 0
  | q, N+1 => rowsQ q + asum ((q+1)%3) N

/-- Any number of consecutive cycles, in the infinite plane: if the plane carries the window of phase `q`, height index `n`, with
    blank west and blank outside the window's rows (east arbitrary), then after `tsum q n N` steps it carries the window of phase
    `(q+N) mod 3`, height index `n+N`, in the same sense, and the ant stands where that window says. -/
theorem forever (N : Nat) : ∀ (q n : Nat) (ox oy : Int) (p : Int → Int → Nat), q < 3 →
    Good ox oy (initQ q n).g p →
    let r := runP (tsum q n N) ⟨p, ox + (initQ q n).x, oy + (initQ q n).y, (initQ q n).h⟩
    r.x = (ox - 3 * (N : Int)) + (initQ ((q+N)%3) (n+N)).x ∧
    r.y = (oy - (asum q N : Int)) + (initQ ((q+N)%3) (n+N)).y ∧
    r.h = (initQ ((q+N)%3) (n+N)).h ∧
    Good (ox - 3 * (N : Int)) (oy - (asum q N : Int)) (initQ ((q+N)%3) (n+N)).g r.p := by
  induction N with
  | zero =>
    intro q n ox oy p hq hG
    have e : q % 3 = q := Nat.mod_eq_of_lt hq
    simp only [tsum, asum, runP, Nat.add_zero, e, Int.natCast_zero, Int.mul_zero, Int.sub_zero]
    exact ⟨trivial, trivial, trivial, hG⟩
  | succ N ih =>
    intro q n ox oy p hq hG
    obtain ⟨h1x, h1y, h1h, h1G⟩ := good_step q n hq ox oy p hG
    have e : runP (clockQ q n) ⟨p, ox + (initQ q n).x, oy + (initQ q n).y, (initQ q n).h⟩ =
        ⟨(runP (clockQ q n) ⟨p, ox + (initQ q n).x, oy + (initQ q n).y, (initQ q n).h⟩).p,
          (ox - 3) + (initQ ((q+1)%3) (n+1)).x, (oy - (rowsQ q : Int)) + (initQ ((q+1)%3) (n+1)).y,
          (initQ ((q+1)%3) (n+1)).h⟩ := by
      rw [← h1x, ← h1y, ← h1h]
    have hq' : (q + 1) % 3 < 3 := Nat.mod_lt _ (by omega)
    have ih' := ih ((q+1)%3) (n+1) (ox - 3) (oy - (rowsQ q : Int))
      (runP (clockQ q n) ⟨p, ox + (initQ q n).x, oy + (initQ q n).y, (initQ q n).h⟩).p hq' h1G
    simp only [tsum]
    rw [runP_add, e]
    have e1 : (q + (N + 1)) % 3 = ((q + 1) % 3 + N) % 3 := by omega
    have e2 : n + (N + 1) = n + 1 + N := by omega
    rw [e1, e2]
    obtain ⟨ix, iy, ih3, iG⟩ := ih'
    refine ⟨by rw [ix]; push_cast; omega, by rw [iy]; simp only [asum]; push_cast; omega, ih3, ?_⟩
    have ex : ox - 3 * ((N + 1 : Nat) : Int) = ox - 3 - 3 * (N : Int) := by push_cast; omega
    have ey : oy - (asum q (N + 1) : Int) = oy - (rowsQ q : Int) - (asum ((q+1)%3) N : Int) := by
      simp only [asum]; push_cast; omega
    rw [ex, ey]
    exact iG

/-- The ideal plane for a window: the window's colours inside it, colour 0 everywhere else. -/
def idealPlane (g : List Row) (ox oy : Int) : Int → Int → Nat :=
  fun a b => (cell? g (a - ox) (b - oy)).getD 0

theorem good_ideal (g : List Row) (ox oy : Int) : Good ox oy g (idealPlane g ox oy) := by
  refine ⟨?_, ?_, ?_⟩
  · intro x y c hc
    simp only [idealPlane]
    have e1 : ox + x - ox = x := by omega
    have e2 : oy + y - oy = y := by omega
    rw [e1, e2, hc]
    rfl
  · intro a b ha
    simp only [idealPlane]
    rw [cell?_none_of_col_neg g (a - ox) (b - oy) (by omega)]
    rfl
  · intro a b ha hb
    simp only [idealPlane]
    rcases hb with hb | hb
    · rw [cell?_none_of_row_neg g (a - ox) (b - oy) (by omega)]
      rfl
    · rw [cell?_none_of_row_ge g (a - ox) (b - oy) (by omega)]
      rfl

/-- Persistence in the ideal infinite plane: starting from the window of phase `q`, height index `n` on an otherwise blank plane,
    for every number `N` of cycles, after `tsum q n N` steps the plane carries the next window in the same sense. -/
theorem forever_ideal (N q n : Nat) (hq : q < 3) :
    let r := runP (tsum q n N) ⟨idealPlane (initQ q n).g 0 0, (initQ q n).x, (initQ q n).y, (initQ q n).h⟩
    Good (-(3 * (N : Int))) (-(asum q N : Int)) (initQ ((q+N)%3) (n+N)).g r.p := by
  have h := forever N q n 0 0 (idealPlane (initQ q n).g 0 0) hq (good_ideal _ 0 0)
  simpa using h.2.2.2

end Sweeper
