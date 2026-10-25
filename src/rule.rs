use std::fmt;
use std::str::FromStr;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Turn {
    L,
    R,
}

impl Turn {
    /// Change in heading, in quarter turns clockwise.
    pub fn delta(self) -> u8 {
        match self {
            Turn::R => 1,
            Turn::L => 3,
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct Rule(pub Vec<Turn>);

impl Rule {
    pub fn len(&self) -> usize {
        self.0.len()
    }

    pub fn is_empty(&self) -> bool {
        self.0.is_empty()
    }

    /// Rule from the low `n` bits of `bits`; bit i set means colour i turns R.
    pub fn from_bits(bits: u32, n: usize) -> Rule {
        Rule(
            (0..n)
                .map(|i| if bits >> i & 1 == 1 { Turn::R } else { Turn::L })
                .collect(),
        )
    }

    /// Swapping every L for R yields the mirror-image ant, so only one of each
    /// pair is interesting. We keep the one starting with R.
    pub fn is_canonical(&self) -> bool {
        self.0.first() == Some(&Turn::R)
    }

    /// Rules where every colour turns the same way just spin in a 2x2 square.
    pub fn is_trivial(&self) -> bool {
        self.0.windows(2).all(|w| w[0] == w[1])
    }
}

impl fmt::Display for Rule {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        for t in &self.0 {
            f.write_str(match t {
                Turn::L => "L",
                Turn::R => "R",
            })?;
        }
        Ok(())
    }
}

impl FromStr for Rule {
    type Err = String;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let turns = s
            .chars()
            .map(|c| match c {
                'L' | 'l' => Ok(Turn::L),
                'R' | 'r' => Ok(Turn::R),
                other => Err(format!("bad turn {other:?}")),
            })
            .collect::<Result<Vec<_>, _>>()?;
        if turns.len() < 2 || turns.len() > 255 {
            return Err("rule must have 2..=255 colours".into());
        }
        Ok(Rule(turns))
    }
}

impl Rule {
    /// Shortest `u` with `self == u^k`. A repeated rule has dynamics identical
    /// to its root (the colour only matters modulo `|u|`), so counting both
    /// double-counts one ant.
    pub fn root(&self) -> Rule {
        let n = self.len();
        for p in 1..n {
            if n.is_multiple_of(p) && self.0[..p].repeat(n / p) == self.0 {
                return Rule(self.0[..p].to_vec());
            }
        }
        self.clone()
    }

    pub fn is_primitive(&self) -> bool {
        self.root().len() == self.len()
    }
}
