from pathlib import Path
p=Path('examples/boundary_return_map_sampler.rs')
s=p.read_text().replace('boundary_return_map_v1','single_cell_gate_v1')
s=s.replace('    cens: bool,','    cens: bool,\n    reach: u64,')
s=s.replace('    let mut t = 0u64;','    let mut t = 0u64;\n    let start = pos;\n    let width = off[2].unsigned_abs().max(off[0].unsigned_abs()).max(off[1].unsigned_abs()).max(off[3].unsigned_abs());\n    let mut reach = 0;')
s=s.replace('        t += 1;\n        if !inner[pos]', '        t += 1;\n        reach = reach.max((pos % width).abs_diff(start % width).max((pos / width).abs_diff(start / width)) as u64);\n        if !inner[pos]')
s=s.replace('cens: false }','cens: false, reach }').replace('cens: true }','cens: true, reach }')
s=s.replace('if !r.overflow && taken[st]', 'if st == 3 && !r.overflow && taken[st]')
s=s.replace('                    row.1.push_str', '                    assert!(ok, "live replay mismatch {spec}");\n                    row.1.push_str')
s=s.replace('spec,band,dep,r,rep,t,dx,dy,h,c,cens,ident,coarse,unexposed,changed','spec,band,dep,pair,arm,cell,match_n,base_t,base_reach,t,reach,cens,ident')
a=s.index('    // cells sorted by depth class')
b=s.index('    let row = format!',a)
s=s[:a]+'''    // Rank baseline read traffic, never perturbation outcomes.
    let mut traffic = vec![0u64; c0.len()];
    let mut c = c0.clone();
    let mut ww = w.clone();
    let (mut pp, mut hh) = (lp, heading);
    for _ in 0..base.t {
        traffic[pp] += 1;
        ww.step(&mut c[pp], &mut hh);
        pp = (pp as isize + loff[hh as usize]) as usize;
    }
    let mut ranked: Vec<usize> = (0..c0.len()).filter(|&i| traffic[i]>0 && inner[i]).collect();
    ranked.sort_by_key(|&i| (std::cmp::Reverse(traffic[i]), i));
    ranked.truncate(3);
    let dist = |i: usize| (i % cw).abs_diff(lp % cw).max((i / cw).abs_diff(lp / cw));
    let mut rng = spec_hash ^ ((band as u64)<<56) ^ ((dep_i as u64)<<32) ^ 2026102201;
    let mut used = ranked.clone();
    let mut arms: Vec<(usize, &str, usize, u8, usize)> = vec![(99,"sham",lp,c0[lp],1)];
    for (k,&g) in ranked.iter().enumerate() {
        let pool: Vec<usize> = (0..c0.len()).filter(|i| inner[*i] && traffic[*i]>0 && !used.contains(i) && c0[*i]==c0[g] && depth[*i]/8==depth[g]/8 && dist(*i)/8==dist(g)/8).collect();
        if pool.is_empty() {
            let _ = writeln!(rep,"{spec},{band},{dep_i},{k},missing,{g},0,{},{},0,0,0,0",base.t,base.reach);
            continue;
        }
        let h = pool[(splitmix(&mut rng) % pool.len() as u64) as usize];
        used.push(h);
        let options: Vec<u8> = (0..resp.len()).filter(|&i| resp[i]!=255 && resp[i]!=resp[c0[g] as usize]).map(|i| i as u8).collect();
        let v = if options.is_empty() {c0[g]} else {options[(splitmix(&mut rng)%options.len() as u64) as usize]};
        arms.push((k,"gate",g,v,pool.len()));
        arms.push((k,"matched",h,v,pool.len()));
    }
    if let Some(i) = (0..c0.len()).find(|&i| inner[i] && traffic[i]==0) {
        let v = (0..resp.len()).find(|&v| resp[v]!=255 && resp[v]!=resp[c0[i] as usize]).unwrap_or(c0[i] as usize) as u8;
        arms.push((99,"offpath",i,v,1));
    }
    for (k,arm,i,v,mn) in arms {
        let mut cc = c0.clone(); cc[i]=v;
        let mut path = vec![false;c0.len()];
        let e = episode(w,&mut cc,&inner,loff,lp,heading,cfg.cap,Some(&mut path));
        let ident = e.t==base.t && e.pos==base.pos && e.heading==base.heading && e.reach==base.reach;
        if arm=="sham" || arm=="offpath" || spec.starts_with("rw:") {assert!(ident,"negative control failed");}
        let _ = writeln!(rep,"{spec},{band},{dep_i},{k},{arm},{i},{mn},{},{},{},{},{},{}",base.t,base.reach,e.t,e.reach,e.cens as u8,ident as u8);
    }
''' +s[b:]
Path('examples/single_cell_gates.rs').write_text(s)
