/-! Task C3: a list-of-rows model of the RLRLLL ant, the frame (embedding) lemma, and the iteration theorems.
    Rows are lists of colours for the columns x = -3 .. 47 (index x + 3). A step that would read outside the rows or the
    columns fails (`none`); that is how "the ant never reads a row the lemma does not own" is expressed. -/
namespace Sweeper

abbrev Row := List Nat

structure St where
  g : List Row
  x : Int
  y : Int
  h : Nat
  deriving DecidableEq, Repr

/-- RLRLLL: colours 0 and 2 turn right (+1 quarter turn), colours 1, 3, 4, 5 turn left (+3). -/
def turn (c : Nat) : Nat := if c = 0 ∨ c = 2 then 1 else 3

/-- Heading 0 = north (y - 1), 1 = east, 2 = south (y + 1), 3 = west; y grows downwards. -/
def dx : Nat → Int
  | 0 => 0
  | 1 => 1
  | 2 => 0
  | _ => -1

def dy : Nat → Int
  | 0 => -1
  | 1 => 0
  | 2 => 1
  | _ => 0

def cell? (g : List Row) (x y : Int) : Option Nat :=
  if 0 ≤ y ∧ 0 ≤ x + 3 then (g[y.toNat]?).bind (fun r => r[(x + 3).toNat]?) else none

def setCell (g : List Row) (x y : Int) (c : Nat) : List Row :=
  g.set y.toNat ((g.getD y.toNat []).set (x + 3).toNat c)

def step (s : St) : Option St :=
  match cell? s.g s.x s.y with
  | none => none
  | some c =>
    let h' := (s.h + turn c) % 4
    some { g := setCell s.g s.x s.y ((c + 1) % 6), x := s.x + dx h', y := s.y + dy h', h := h' }

/-- Exactly `k` steps, or failure if any of them would read outside the rows. -/
def runN : Nat → St → Option St
  | 0, s => some s
  | k + 1, s => (step s).bind (runN k)

theorem runN_add (a b : Nat) (s : St) : runN (a + b) s = (runN a s).bind (runN b) := by
  induction a generalizing s with
  | zero => simp [runN]
  | succ a ih =>
    have : a + 1 + b = (a + b) + 1 := by omega
    rw [this]
    simp only [runN]
    cases step s with
    | none => simp
    | some s' => simp [ih]

/-- Put `pre` above and `post` below the rows of a state; rows are numbered from the top of `pre`. -/
def emb (pre post : List Row) (s : St) : St :=
  { g := pre ++ s.g ++ post, x := s.x, y := s.y + pre.length, h := s.h }

theorem cell?_inv (g : List Row) (x y : Int) (c : Nat) (h : cell? g x y = some c) :
    0 ≤ y ∧ 0 ≤ x + 3 ∧ y.toNat < g.length ∧ ∃ r, g[y.toNat]? = some r ∧ r[(x + 3).toNat]? = some c := by
  unfold cell? at h
  by_cases hc : 0 ≤ y ∧ 0 ≤ x + 3
  · rw [if_pos hc] at h
    cases hr : g[y.toNat]? with
    | none => simp [hr] at h
    | some r =>
      simp only [hr, Option.bind_some] at h
      exact ⟨hc.1, hc.2, (List.getElem?_eq_some_iff.mp hr).1, r, rfl, h⟩
  · rw [if_neg hc] at h
    simp at h

theorem cell?_emb (pre post g : List Row) (x y : Int) (c : Nat)
    (h : cell? g x y = some c) : cell? (pre ++ g ++ post) x (y + pre.length) = some c := by
  obtain ⟨hy, hx, hlt, r, hr, hrc⟩ := cell?_inv g x y c h
  unfold cell?
  have hc' : 0 ≤ y + (pre.length : Int) ∧ 0 ≤ x + 3 := ⟨by omega, hx⟩
  rw [if_pos hc']
  have hi : (y + (pre.length : Int)).toNat = y.toNat + pre.length := by omega
  rw [hi]
  have hr' : (pre ++ g ++ post)[y.toNat + pre.length]? = some r := by
    rw [List.append_assoc, List.getElem?_append_right (by omega), Nat.add_sub_cancel, List.getElem?_append_left hlt]
    exact hr
  rw [hr']
  simpa using hrc

theorem setCell_emb (pre post g : List Row) (x y : Int) (c : Nat) (hy : 0 ≤ y) (hlt : y.toNat < g.length) :
    setCell (pre ++ g ++ post) x (y + pre.length) c = pre ++ setCell g x y c ++ post := by
  unfold setCell
  have hi : (y + (pre.length : Int)).toNat = y.toNat + pre.length := by omega
  rw [hi]
  have e1 : (pre ++ g ++ post).getD (y.toNat + pre.length) [] = g.getD y.toNat [] := by
    rw [List.append_assoc]
    simp [List.getD_eq_getElem?_getD, List.getElem?_append_right, List.getElem?_append_left hlt]
  rw [e1]
  rw [List.append_assoc, List.append_assoc]
  rw [List.set_append_right _ _ (by omega)]
  simp only [Nat.add_sub_cancel]
  rw [List.set_append_left _ _ hlt]

theorem step_emb (pre post : List Row) (s s' : St) (h : step s = some s') :
    step (emb pre post s) = some (emb pre post s') := by
  unfold step at *
  cases hc : cell? s.g s.x s.y with
  | none => simp [hc] at h
  | some c =>
    simp only [hc] at h
    obtain ⟨hy, hx, hlt, _⟩ := cell?_inv s.g s.x s.y c hc
    have hc2 : cell? (emb pre post s).g (emb pre post s).x (emb pre post s).y = some c := cell?_emb pre post s.g s.x s.y c hc
    simp only [hc2]
    simp only [Option.some.injEq] at h
    subst h
    have e1 := setCell_emb pre post s.g s.x s.y ((c + 1) % 6) hy hlt
    simp only [emb, e1, Option.some.injEq, St.mk.injEq]
    refine ⟨trivial, trivial, ?_, trivial⟩
    exact Int.add_right_comm _ _ _

theorem runN_emb (pre post : List Row) (k : Nat) (s s' : St) (h : runN k s = some s') :
    runN k (emb pre post s) = some (emb pre post s') := by
  induction k generalizing s with
  | zero => simp [runN] at h; subst h; simp [runN]
  | succ k ih =>
    simp only [runN] at h ⊢
    cases hs : step s with
    | none => simp [hs] at h
    | some s1 =>
      simp only [hs, Option.bind_some] at h
      rw [step_emb pre post s s1 hs]
      simp only [Option.bind_some]
      exact ih s1 h

end Sweeper
