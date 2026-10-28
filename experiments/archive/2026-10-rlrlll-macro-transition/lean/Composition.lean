import Model

namespace Sweeper

/-- Rename old x to x+3, retain the next window's columns 0..47, and
    give its three western context columns colour zero. -/
def shiftRow (r : Row) : Row := [0, 0, 0] ++ r.take 48

theorem replicate_sum (a b : Nat) (r : Row) :
    List.replicate (a+b) r = List.replicate a r ++ List.replicate b r := by
  induction a with
  | zero => simp
  | succ a ih => simpa [Nat.succ_add, List.replicate_succ] using congrArg (List.cons r) ih

theorem map_band (rpp : List Row) (bulk : Row)
    (h : rpp.map shiftRow = [bulk, bulk]) (n : Nat) :
    ((List.replicate n rpp).flatten).map shiftRow = List.replicate (2*n) bulk := by
  induction n with
  | zero => simp
  | succ n ih =>
    simp only [List.replicate_succ, List.flatten_cons, List.map_append, h, ih]
    have he : 2*(n+1) = 2*n+1+1 := by omega
    simp [he, List.replicate_succ]

/-- The finite end equalities and one band equality suffice for all n.
    No inference from a finite sample of heights is used. -/
theorem compose_band (E D rpp pre post : List Row) (bulk : Row) (a b : Nat)
    (he : E.map shiftRow = pre ++ List.replicate a bulk)
    (hd : D.map shiftRow = List.replicate b bulk ++ post)
    (hr : rpp.map shiftRow = [bulk, bulk]) (n : Nat) :
    (E ++ (List.replicate n rpp).flatten ++ D).map shiftRow =
      pre ++ List.replicate (a + 2*n + b) bulk ++ post := by
  simp only [List.map_append, he, hd, map_band rpp bulk hr n]
  simp only [replicate_sum, List.append_assoc]

end Sweeper
