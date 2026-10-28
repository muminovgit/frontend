// Single source of truth for timing: the composition reads it for picture,
// tools/score.py reads the same file (via node) for music + SFX placement.
(function (root) {
  var CUES = {
    dur: 15,
    // hard background switches
    dark: 5.2,
    light: 8.7,
    // S1 everyday purchases
    s1Land: [0.3, 0.62, 0.94],
    s1Exit: 1.62,
    // S2 1+1
    oneL: 1.95,
    plus: 2.12,
    oneR: 2.28,
    loop: [2.42, 2.9],
    s2Exit: 3.45,
    // S3 the coin flies (drums out while airborne)
    coinPop: 3.4,
    launch: 3.55,
    chegLand: 4.42,
    // S4 dark: QR
    phoneIn: 5.2,
    qrType: [5.55, 5.8],
    lock: 6.05,
    s4Exit: 7.0,
    // S5 coins
    coinType: [7.15, 7.4],
    rain: [7.3, 7.41, 7.52, 7.63, 7.74, 7.85, 7.96],
    // S6 places reel
    reel: [8.8, 9.12, 9.44, 9.76, 10.08],
    // S7 three verbs
    verbs: [10.5, 10.85, 11.2],
    s7Exit: 12.05,
    // S8 logo
    logoDrop: 12.3,
    logoLand: 12.62,
    wordWipe: 12.78,
    footer: 14.3,
  };
  if (typeof module !== "undefined") module.exports = CUES;
  else root.CUES = CUES;
})(this);
