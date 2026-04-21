Recalibrate the reserved-instance discount multipliers in index.html.

Background: this static one-pager shows EC2 on-demand pricing pulled live from
AWS's JSON feed, plus an estimated "Reserved 1yr Convertible (no-upfront)"
column computed as priceMonthly * reservedMultiplier(instanceType). The
multiplier table lives in a `reservedDiscounts` object inside the <script>
block in index.html (search for "reservedDiscounts"). It's keyed by instance
family prefix (letters before the first digit: "r7a" -> "r", "inf2" -> "inf",
"hpc7a" -> "hpc", "mac2" -> "mac"). Families not in the table fall back to
0.73 via the `??` in reservedMultiplier().

Task:
1. Download Vantage's consolidated pricing JSON (this is the only compact
   public source for RI prices that covers every instance type):
     curl -s --compressed https://instances.vantage.sh/instances.json -o /tmp/vant.json
   Size is ~17 MB gzipped / ~200 MB uncompressed. JSON is a list; each entry
   has .instance_type and .pricing[region][os].{ondemand, reserved}, where
   reserved is a dict with keys like "yrTerm1Convertible.noUpfront".

2. For each instance, compute ratio = yrTerm1Convertible.noUpfront / ondemand
   in region us-east-2, OS "linux". Group by family prefix (regex ^[a-z]+
   applied to the part before the "."). Take the MEDIAN ratio per family.
   Skip families with <3 instances unless they already exist in the current
   table. Round to 2 decimal places.

3. Compare the new medians to the current `reservedDiscounts` table. Show me
   a diff-style summary (family, old, new, delta) before editing. If any
   family moved by >0.03, flag it.

4. After I confirm, update the `reservedDiscounts` object in index.html with
   the new values. Preserve the comment above it; update the date in that
   comment to today's month/year. Don't touch anything else in the file.

5. Sanity-check: pick 3 random instance types (one small, one large, one GPU)
   and print "<type>: ondemand=$X, computed_reserved=$Y, vantage_reserved=$Z,
   error=N%". Error should be under ~3% for most; flag any outliers.

Don't add a build step or fetch this data at runtime — the whole point of the
family-table approach is to keep the site as a single static file with no
dependencies beyond AWS's on-demand feed.
