import Lean
open Lean

/-- The kind of a declaration this connector reports, or none. -/
def declKind (env : Environment) (n : Name) : ConstantInfo → Option String
  | .thmInfo _ => some "theorem"
  | .defnInfo _ => some (if Meta.isInstanceCore env n then "instance" else "definition")
  | .inductInfo _ => some (if isStructure env n then "structure" else "inductive")
  | _ => none

/-- Compiler-generated names are not declarations a person wrote. -/
def generated (n : Name) : Bool :=
  n.isInternal || match n with
    | .str _ s => s.startsWith "match_" || s.startsWith "proof_" || s.startsWith "eq_"
    | _ => false

/-- Print one JSON line per requested module and per declaration in those modules. -/
unsafe def main (args : List String) : IO UInt32 := do
  initSearchPath (← findSysroot)
  let wanted : NameSet := args.foldl (fun s a => s.insert a.toName) {}
  let imports := args.toArray.map fun a => ({ module := a.toName } : Import)
  withImportModules imports {} 0 fun env => do
    let hdr := env.header
    for i in [0:hdr.moduleNames.size] do
      let m := hdr.moduleNames[i]!
      if wanted.contains m then
        let imps := hdr.moduleData[i]!.imports.map fun imp => Json.str imp.module.toString
        IO.println (Json.mkObj [("t", "module"), ("name", m.toString), ("imports", Json.arr imps)]).compress
    let inSet (n : Name) : Option Name :=
      match env.getModuleIdxFor? n with
      | some idx => let m := hdr.moduleNames[idx.toNat]!; if wanted.contains m then some m else none
      | none => none
    let all := env.constants.fold (fun acc n ci => acc.push (n, ci)) #[]
    for (n, ci) in all do
      if let some m := inSet n then
        if !generated n then
          if let some kind := declKind env n ci then
            let used := ci.type.getUsedConstants ++ (match ci.value? with | some v => v.getUsedConstants | none => #[])
            let deps := used.foldl (fun (s : NameSet) d =>
              if d != n && !generated d && (inSet d).isSome then s.insert d else s) {}
            let depJson := deps.toList.toArray.map fun d => Json.str d.toString
            IO.println (Json.mkObj [("t", "decl"), ("name", n.toString), ("kind", kind),
              ("module", m.toString), ("deps", Json.arr depJson)]).compress
    return 0
