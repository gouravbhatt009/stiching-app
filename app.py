 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/README.md b/README.md
index a35cb1d24fceafd0be0461fff71ff15c649fc7f1..a6af18e7ceb8924cb83b3cc5038ddf3656406b74 100644
--- a/README.md
+++ b/README.md
@@ -1,7 +1,16 @@
-# Welcome to GitHub Desktop!
+# Stitching Costing Playbook
 
-This is your README. READMEs are where you can communicate what your project is and how to use it.
+This repository now contains a practical blueprint to improve stitching costing reliability for factories managing many employees, style-wise standards, and actual-vs-master variance tracking.
 
-Write your name on line 6, save it, and then head back to GitHub Desktop.
+## Start here
 
-This is a type of data work in the tensor flow during his peak. <br> Author - Gourav bhatt
+- `docs/stitching-costing-environment.md` — complete operating model, data structure, formulas, governance controls, KPIs, and a 30-60-90 implementation plan.
+
+## Why this helps
+
+The framework is designed to make costing more reliable by combining:
+
+- standard (master) time and cost control,
+- daily actual production and expense capture,
+- strict versioning and governance,
+- rapid variance detection with clear ownership.
 
EOF
)
