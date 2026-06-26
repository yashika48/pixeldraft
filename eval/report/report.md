# PixelDraft — Real-World Evaluation

End-to-end results on real screenshots the model never saw during training.

| Screenshot | Elements | Avg confidence | Visual SSIM |
|---|---|---|---|
| dashboard_test.png.jpeg | 27 | 0.633 | n/a |
| design 2.png.jpeg | 28 | 0.639 | n/a |
| design 3.png.jpeg | 15 | 0.593 | n/a |
| design 4.png.jpeg | 20 | 0.734 | n/a |
| design.png.jpeg | 6 | 0.561 | n/a |

## Honest notes
- Trained on synthetic UIs; these are real screenshots, so this is the sim-to-real result.
- Output is a structural starting point, not a pixel-perfect clone.
- OCR and layout degrade on dense/complex real UIs (see failure cases below).
