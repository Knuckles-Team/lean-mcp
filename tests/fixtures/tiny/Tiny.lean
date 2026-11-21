def double (n : Nat) : Nat := n + n

theorem double_eq (n : Nat) : double n = n + n := rfl

structure Point where
  x : Nat
  y : Nat
