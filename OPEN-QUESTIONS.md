# Open questions

1. **Value assembly:** how q, H and L combine into a signed residual. No mapping tried so far beats the trivial baseline.
2. **Predictor:** which neighbours the residual is relative to. The horizontal-gradient lead (see FINDINGS) needs testing by integrating along rows.
3. **Row stride drift:** on some bodies the per-row token count drifts instead of staying equal to the width. Why?
4. **Horizontal offset ramp:** the alignment offset with the preview grows with row band. Is that an artefact of the alignment method or real?
5. **Larger sensors:** the ordinary (non-escape) code in files sharing the 31-bit escape.
6. **Reproduction:** turn each finding into a script in `tools/` that runs on named raw.pixls.us CC0 files.
