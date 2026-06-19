# Referee review: existential_risk
_Tier: A (mature manuscript). Reviewed 2026-06-19._

## Editor's decision

Both referees independently confirm the two facts that decide this paper. First, the gamma>=2 core reproduces exactly: Proposition 1 (cons-channel 754.28, flow-channel 11,666.67, share 0.939) and the headline cutoff are correct, and the closed-form welfare functional matches numerical integration. Second, the gamma=1 (log) case is broken: `social_welfare` (line 91) carries a `g/(D3*D4^2)` term that `welfare_decomposition` (line 151) omits, so the two code paths compute different objects. I verified this directly. At the headline log cell (g_ai=0.10, m_ai=0.005) the coded flow-share is 0.202 but the share consistent with the welfare function that actually sets delta* is 0.094. Every gamma=1 row is affected, and these rows carry the paper's only counter-message ("growth does substantial work under log utility"). That message currently rests on a dropped term.

The referees diverge only on the verdict. Referee 2 recommends Reject, weighting three things as fatal: the bug, thin novelty relative to Jones/Aschenbrenner/Trammell, and the admission that the 94% headline inverts once growth's mortality spillover (the author's own preferred extension) is allowed. Referee 1 recommends Major Revision: the correct gamma>=2 core and a real-if-modest accounting contribution survive, while the bug, the framing, and the load-bearing VSL-to-u_bar mapping are all fixable.

I side with Referee 1. The three issues R2 cites are correctable rather than disqualifying: the bug is a localized derivation error, the inversion is a scoping requirement, and novelty is a judgment the revision can sharpen. The three things that matter most: (1) fix and re-derive the gamma=1 welfare formula, reconcile the two code paths, and regenerate all log rows; (2) reframe the result around the actual u_bar/rho_s mechanism and justify (or honestly bound) the marginal-VSL-to-additive-constant mapping that carries the entire result; (3) implement the mortality-spillover extension and report how far 94% moves, so the headline is externally valid.

**Decision:** Major Revision

## Referee 1

## Summary

The paper poses a representative-agent CRRA economy with a per-period "value-of-being-alive" flow term $\bar u$ calibrated to VSL data, and computes the extinction-hazard cutoff $\delta^*$ at which a transformative-technology scenario equals a status-quo baseline in social welfare. The headline claim is a decomposition result: at standard calibration the welfare gain that $\delta^*$ trades against is ~94% mortality-channel and ~6% growth-channel, so "growth versus extinction" is the wrong framing.

## 1. Contribution and novelty

The genuinely new object is the channel decomposition of the cutoff (eq. 14, Prop. 1). The cutoff concept itself and the CRRA-plus-VSL machinery are standard (Hall-Jones 2007 for the additive value-of-life term; the social-discounting and VSL literatures are decades old). The contribution is therefore a clarifying/accounting result, not a new model or new identification. That is publishable in principle, but the gap as stated is thin: that mortality dominates when $\bar u \approx 7$ swamps $|c_0^{1-\gamma}/(1-\gamma)|=1$ and is divided by a tiny $\rho_s$ is, once written down, close to arithmetic. The paper needs to argue more forcefully why this was not already obvious to the Aschenbrenner/Trammell/Jones literature it cites.

## 2. Correctness

I verified the core derivations against numerical integration. **The closed-form welfare functional (eq. 8) is correct**: the double cohort integral reproduces $W$ to ten digits at $\gamma=2$, and the Proposition 1 numbers (cons-channel 754.28, flow-channel 11,666.67, share 0.939) are exact. The convergence condition $(\rho+m)+(\gamma-1)g>0$ in eq. (7) is correctly stated.

**However, there is a genuine internal-validity error in the $\gamma=1$ (log) case.** The welfare function `social_welfare` (code lines 91) integrates cohorts correctly and includes a cross-cohort growth term $g/(D_3 D_4^2)$. But `welfare_decomposition` (code line 151) **omits that term**, so the consumption-channel gain used to compute the reported flow-share is internally inconsistent with the welfare function used to compute $\delta^*$. Concretely, for the $\gamma=1$, $g_{AI}=10\%$, $m_{AI}=0.5\%$ cell, Table 1 reports flow-share 0.20; the share consistent with the actual $W$ is **0.094**. Every $\gamma=1$ flow-share in Table 1 (0.37, 0.20, 0.11) is affected, and these are exactly the numbers underpinning result (iii) and the §5 reading "at $\gamma=1$ the consumption-channel share is comparable to the flow-utility share." That claim is an artifact of a dropped term, not a property of the model. This must be fixed; the $\gamma=1$ column may change qualitatively.

Hidden-assumption issues that need to be made explicit:

- **The flow term $\bar u$ is unbounded in the discount integral.** Because $\bar u$ is a constant added to every instant of every cohort, $W$ contains a term $\bar u/(\rho_s(\rho+m))$ that diverges as $\rho_s\to0$. The "structural sensitivity to $\rho_s$" (Table 2) and the entire dominance result are driven by this $1/\rho_s$ pole. The decomposition is therefore not a neutral accounting of "what the data say"; it is a near-mechanical consequence of adding a consumption-independent constant to flow utility and dividing by a small pure rate of time preference. §3 ("not an artefact of the functional form") overstates: it is precisely an artefact of the additive-constant device interacting with $D_4=\rho_s$.

- **The VSL calibration of $\bar u$ (eqs. 4–5) is a level-matching of $v(c_0)$, not a derivation from marginal willingness-to-pay for mortality risk.** Eq. (4) defines $v_{c_0}$ as VSL/(LE × consumption), but $\bar u$ is then pinned by $v(c_0)=v_{c_0}$ (eq. 5), i.e. by equating total flow utility to a value-per-life-year. VSL is a marginal object; the paper uses it as a level. The mapping from a marginal-MRS estimate to an additive utility constant is not innocuous and is never justified. Since $\bar u$ carries the whole result, this is the single most important gap.

- **Asymmetric hazard entry (eq. 11).** $\delta$ augments private mortality in $D_1,D_3$ and social discounting in $D_2,D_4$, but with no continuation/rebuilding value and no value placed on the extinction event itself. This is defensible but is an assumption, not a neutral modeling choice, and the binary "civilisation continues vs contributes zero" should be stated as such.

## 3. Do results support the claims?

For $\gamma\ge2$, yes — the numbers are correct and the dominance claim holds. But the headline is over-generalized. The result is conditional on (i) the additive-constant VSL device, (ii) a small pure $\rho_s$, and (iii) $\gamma>1$. The abstract and §6 present "growth buys little hazard tolerance" as a finding about the world; it is a finding about this utility form. The paper's own §6(ii) concedes alternative utility forms would overturn it, which undercuts the strength of the framing. The claim "$\delta^*$ scales proportionally with $\rho_s$" (result iii) is only approximate and is asserted, not proved — Table 2 shows $\delta^*$ falling by ~13× when $\rho_s$ falls by 20×, so "proportional" is loose.

## 4. Framing and exposition

The honesty about the earlier bug (header comment) is commendable. But the paper repeatedly insists the result is "structural, not an artefact of functional form" while the mechanism is transparently the additive constant over $\rho_s$. Reframe around that mechanism rather than denying it. The "definition/proposition" apparatus is heavy for what is direct numerical evaluation; Prop. 1 is a single plug-in, not a theorem.

## 5. Required revisions

1. Fix the $\gamma=1$ decomposition term mismatch; recompute all log-case shares and revisit result (iii).
2. Derive (or honestly bound) $\bar u$ from VSL as a marginal object, or state clearly that you impose a level-matching and show robustness to the mapping.
3. State the $1/\rho_s$ pole explicitly and reframe the $\rho_s$-sensitivity as its consequence; prove or drop the "proportional" claim.
4. Provide a comparative-statics proof of Prop. 1's dominance (sufficient condition on $\bar u/\rho_s$ vs $|c_0^{1-\gamma}/(1-\gamma)|$), so the result is a theorem rather than one calibrated cell.
5. Add monotonicity/uniqueness of the root $\delta^*$ (currently assumed by `brentq`); show $W_{AI}(\delta)$ is monotone so the cutoff is well-defined.

**Recommendation:** Major Revision — the $\gamma\ge2$ core is correct and the decomposition is a real if modest contribution, but a confirmed internal inconsistency in the log case, an unjustified VSL-to-$\bar u$ mapping that carries the entire result, and over-claimed "not-an-artefact" framing must be resolved before the headline can stand.

## Referee 2

**Manuscript:** "Mortality, Growth, and the Existential-Risk Cutoff"

## Summary

The paper builds a CRRA representative-agent welfare functional augmented with a VSL-calibrated additive flow benefit $\bar u$, adds an extinction hazard $\delta$ as a Poisson discount increment, and solves numerically for the cutoff $\delta^*$ at which a transformative scenario matches a status-quo baseline. The headline claim is a decomposition result: at standard calibrations ~94% of the welfare gain runs through the mortality (flow-utility) channel, so the cutoff is "about life-years preserved," not growth.

## 1. Contribution and novelty

The decomposition framing is the paper's only genuinely novel move, and it is a modest one. Everything upstream (CRRA + VSL-calibrated value of a life-year, cohort aggregation, hazard-as-discount-increment) is standard and is acknowledged as such (Sec. 2, the Hall-Jones / Murphy-Topel lineage cited at l.81). The "which channel does the work" question (l.59) is reasonable, but the answer is close to mechanical: once you put a large additive constant $\bar u \approx 7$ over a tiny denominator $D_4=\rho_s=0.01$, the flow term necessarily swamps a consumption term of order 1. The author essentially concedes this in Sec. 2 ("not an artefact of the functional form") and again at l.178-180, but the rebuttal is unconvincing: $\bar u/\rho_s$ dominating $c^{1-\gamma}/(1-\gamma)$ *is* a functional-form fact, not a fact about the world. The "gap" relative to Aschenbrenner/Trammell/Jones is real only in the narrow sense that those papers are endogenous-growth and this is a static cost-benefit; but a static recalculation that reproduces a known force (life-years dominate at low discount rates) is thin for a top-5 outlet.

## 2. Correctness

I checked the code (`code/existentialrisk.py`) against the manuscript.

- **Proposition 1 (l.182-189) is correct.** I reproduced cons-channel $=754.28$, flow-channel $=11{,}666.67$, share $=0.939$. The Table 1 / discount / VSL numbers also reconcile once one notices the tables are in percent (so code's $\delta^*=0.002015$ = "0.201 %/yr"). State this units convention explicitly; right now the abstract's "a fifth of a percent" and the table's "0.201" look contradictory and cost the reader trust.

- **The $\gamma=1$ (log) case is derived incorrectly, and the two code paths disagree with each other.** The true cohort-integrated log consumption welfare at $(g,m,\rho_s)=(0.10,0.01,0.01)$ is $74{,}283$ (numerical double integral). `social_welfare` returns $75{,}000$; `welfare_decomposition` returns $25{,}000$ (it drops the $g/(D_3 D_4^2)$ term present in the former). So every $\gamma=1$ row in Table 1 and every $\gamma=1$ flow-share is built on a mis-derived and internally inconsistent welfare object. This matters because the $\gamma=1$ rows carry the paper's only counter-message — that "growth does substantial work under log utility" (l.244). That claim currently rests on a bug. This must be fixed and the table regenerated before any judgment about the log case can stand.

- **Hidden inconsistency in the hazard's two roles (eq. 6, l.149-154).** $\delta$ is added to *both* private mortality ($\rho+m+\delta$ in $D_1,D_3$) and social discounting ($\rho_s+\delta$ in $D_2,D_4$). This double-counts: the Poisson extinction event is a single aggregate event, yet here it discounts the within-cohort flow *and* the cross-cohort measure independently, as if individual death and civilizational extinction were independent risks. The economic justification (l.149) is asserted, not derived. Because $\delta$ enters $D_4=\rho_s+\delta$ — the term the whole result is sensitive to — this modelling choice is load-bearing and needs a microfoundation.

- **The decomposition is evaluated at $\delta=0$ only (eq. 8).** The "94%" describes the *level* gain $W_{AI}(0)-W_0$, not the *marginal* trade-off that actually sets $\delta^*$ ($dW_{AI}/d\delta$ at the root). The paper repeatedly elides these (l.191, l.267 hand-waves the ratio "scales approximately with $\rho_s$"). The headline "the cutoff inherits the channel dominance" is asserted, not proven.

## 3. Do results support the headline claims?

Partially, and with over-claiming. "Growth buys little hazard tolerance" is robust at $\gamma\ge 2$ in the (correct) CRRA rows. But the abstract/conclusion sell this as a substantive economic finding ("the relevant debate is not growth versus extinction") when, as Sec. 5(ii) admits, it is an artefact of routing all of growth's welfare value through consumption and none through mortality — even though the paper itself notes growth historically *reduces* mortality (l.304). Once that channel is allowed, the headline can invert. A result that flips under the author's own stated, empirically-preferred extension is not ready to be a policy headline.

## 4. Framing and exposition

The "methodological positioning" paragraphs (l.71, l.314) are honest to the point of undercutting the paper: the author lists three things the framework cannot do, two of which (mortality-growth complementarity, learning/irreversibility) are exactly what would change the answer. Sec. 2's "What carries the result" is good practice. But the paper has no figure (a $\delta^*$-vs-$\rho_s$ and channel-share plot would communicate the whole result), and Definition 1 asserts the single-crossing/monotonicity of $W_{AI}(\delta)$ without proof — needed for $\delta^*$ to be well-defined.

## 5. Required revisions

1. Fix and re-derive the $\gamma=1$ welfare formula; reconcile `social_welfare` and `welfare_decomposition`; regenerate all log rows.
2. Microfound the dual entry of $\delta$ into private and social discounting (eq. 6); show it is not double-counting.
3. Prove $W_{AI}(\delta)$ is monotone so $\delta^*$ is unique (Def. 1).
4. Make the level-vs-marginal distinction explicit; prove (not assert) that the cutoff inherits the channel share and the $\rho_s$ scaling.
5. State the percent units convention in every table.
6. Implement at least the mortality-spillover-of-growth extension (l.302b) and report how far the 94% moves; without it the headline is not externally valid.
7. Add a figure; sharpen the contribution relative to Jones (2024).

**Recommendation:** Reject — the central decomposition is largely a restatement of a known $\bar u/\rho_s$ mechanism, the headline inverts under the author's own preferred extension, and a load-bearing case (log utility) rests on a mis-derived, internally inconsistent welfare formula; this is below the novelty and correctness bar for a top-5 journal.
