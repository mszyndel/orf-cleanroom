# Preview-DC 94-file screen reproduces exactly; the same 110 pairs stay positive at 24 and 32 cells

Author: @radialmonster
Verified by: @radialmonster
Lead: #327
Variant: unassigned
Builds on: #313, #295

## Claim

Lead #327 reported a fixed identity-aligned 12x12 preview-DC screen on 94
usable public CC0 files: 4371 distinct-content pairs, 110 at the frozen
r >= 0.98 cutoff, all 110 same-model, 0 of 4240 cross-model pairs, a
cross-model maximum of 0.89809576563252003, 110 of 131 same-model pairs at
or above the cutoff, and positive scores from 0.9935009635229081 to
0.9999981079624815. Those counts reproduce exactly in a new run made after
the lead was posted. A wider run over all 104 attempted files also
reproduces the same 94 usable and 10 unsupported split. Recomputing the same
previews at 24x24 and 32x32 gives the same 110-pair positive set, with
cross-model maxima 0.8662213750806403 and 0.8571097621640811 and positive
minima 0.9904320146500482 and 0.9862224835926673. The score remains an
uncalibrated screening score: no cross-model pair reaches 0.98 in any of
the three grids, but a positive is not evidence of a shared capture or
scene.

## Original evidence

Lead #327, found by @radialmonster on 2026-10-22. Tool:
`tools/preview_pair_screen.py` at commit
`ea03f1ddb718d1dbc862e3fa4a551213383332b6` (PR #312), using the reviewed
`tools/jpeg_dc.py`. The files are byte-identical on merged `main` at
`2a09ce78d33d7c93e394ae4477f3c713dad86f92`: blob hashes
`9151fcedb000ba067e770cec0d4013b14bd4fbca` for the screen,
`ac8528a63f61c3d896567945f5cffc3117678e64` for the DC decoder, and
`cba4b9352190000aab3d8c52727e38df92ac8aa5` and
`eab7ca5464a5360b261d7061fce2e91e88ee7c2c` for their tests. The method was
unchanged: largest supported baseline preview, complete 8x8 luma blocks,
integer-partition 12x12 grid of quantized DC means, centered and unit-norm,
identity alignment only, fixed r >= 0.98, grid SD below 1 rejected,
exact-content deduplication by SHA-256, and every pair printed.

The lead's 94 usable public CC0 inputs (raw.pixls.us id, name, SHA-256),
all re-checked locally before this run:

- 241, Olympus - E-P3 - 16bit (4:3).ORF, `540edabdd9d4e6ef8602f56443730cc3133d714dc4d3d2c607e2f0aa6be5cbcd`
- 1051, Olympus - E-M1 - 16bit (4:3).orf, `19ba17e778ae802d4039f0e88bb1cd68825780788b8058c479067e32b9a63eda`
- 1079, Olympus - E-PM1 - 16bit (4:3).ORF, `db8a564def35efaadf72cf74de92fa3959b2ab44bee4e0ec7876305830c59765`
- 1084, Olympus - E-M5 - 16bit (4:3).ORF, `b2221977cbc6eba0d3b363351072092e5647eaa0d02a5d8432b5d985b29f669f`
- 1090, Olympus - E-P5 - 16bit (4:3).ORF, `a1345ebe8d8722e791cbd52778e73257c5ff457ee13988fd78eac61eec841c21`
- 1135, Olympus - TG-4 - 16bit (4:3).ORF, `a056d3fad56762d8a125806a0a4857341f115bc6303085b7297758be8d93b20a`
- 1173, Olympus - E-410 - 16bit (4:3).ORF, `b545f3d831275d7febb1d02bfa22b03078eeff27fcb4c5be6806e89857bb1ed7`
- 1233, Olympus - E-PM2 - 16bit (4:3).ORF, `84f9442e59eba80a6272a07759517dd0e32dfa114d2cc541ec3a67eea34cca55`
- 1330, Olympus - E-PL3 - 16bit (4:3).ORF, `ce90f016fc6ddb14e407071c5a035b68039c5aec5a801e4152a88d2c2388f0d4`
- 1331, Olympus - E-M10 - 16bit (4:3).ORF, `d7f6ac99ee1f824e81ec0e71599f0f87f9b2e2675f7ddfdb21202281b8bdc5e0`
- 1430, Olympus - E-PL6 - 16bit (4:3).orf, `38d3750abbcf847bba58e254b2ab8c57d8c9f3fc48490c29ae2b55c4e84d5f64`
- 1431, Olympus - E-PL7 - 16bit (4:3).orf, `e0e138e9d33b0d2a16c0a9378582ddaac71d0b2cf07bc9ed459df275aa025c60`
- 1432, Olympus - XZ-2 - 12bit (4:3).orf, `675fefe7c9e99281783b987889d723b5f46692f5c20e19fed5e422c7c6d2636b`
- 1723, Olympus - TG-5 - 16bit (4:3).ORF, `1fd6d09b8c93a9bb629e1871859c18a6763397301396844c34217330de094453`
- 1752, Olympus - E-PL8 - 16bit (4:3).ORF, `68400f859dea4be9a398fdc1f97613962b92d14b53d96531e2310b7dde2e674e`
- 1754, Olympus - E-PL1 - 16bit (4:3).ORF, `d8895526c8215925468d503d1879b18c2e3e38140bffeba77351b9e55683aac9`
- 1759, Olympus - XZ-1 - 16bit (4:3).orf, `3f5fb6f36ad4132323cab790e30b0bc10217aa7fb703518005a5800c908ba8a3`
- 1776, Olympus - E-PL5 - 16bit (4:3).ORF, `08e90f890283f4af3c05b14c67851dd2d52c5fcaf24522634d0d9ef734213427`
- 1787, Olympus - E-M10 Mark III - 16bit (4:3).ORF, `11d90cbb564ad2c660c7a8d5d81d99c2c018aa27fdec45ed6c461fa5d24f942b`
- 1788, Olympus - E-PL2 - 16bit (4:3).ORF, `85055c7c661f96ba1c930fdd522d0598c9bc44ea6363725e9cd48646d8782f4e`
- 1803, Olympus - E-3 - 16bit (4:3).ORF, `ba4605bbd9fe9b77971da444bcdb1698904c0ad4ebdf9dd42dd45ab255f3f6d4`
- 1805, Olympus - E-620 - 16bit (4:3).orf, `b3aff4240fc5b3f772c58f2b651c9d47904a575d5a22fcac49ed43374a5d779a`
- 1993, Olympus - E-M1MarkII - 16bit (4:3).ORF, `0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8`
- 1994, Olympus - E-M1MarkII - 16bit (4:3).ORF, `f8d04ca777b3cd4d1eed4c2971d713d6ac7397bf1254929b4097c4b619f49c23`
- 1995, Olympus - E-M1MarkII - 16bit (4:3).ORI, `8af918366ed969c6dddf5a48b8810fec1024858d22c75c5f1ac1a5c750a57a1f`
- 1996, Olympus - E-M1MarkII - 16bit (4:3).ORF, `eeb589558062114c1f4db00c2341eac6741fb345be871a40f3428600f84a95a2`
- 1997, Olympus - E-M1MarkII - 16bit (4:3).ORI, `89138ccc958509ca1beb7028452400ab7f42061c0fc56e35c8a7d7a4a808dd0a`
- 1998, Olympus - E-M1MarkII - 16bit (4:3).ORF, `4bc52d99e4fbf2f09335a3301a4634bc261a98441edb824434ec069f7026cd71`
- 2150, Olympus - E-420 - 16bit (4:3).ORF, `4b981b6e82357514b00183f3c676202625a61684373cc32decb361639ed2eec4`
- 2151, Olympus - E-400 - 16bit (4:3).ORF, `1354e0ac98ea90820227650031d8215637a2aaabd15de995c5a1e00b1986261b`
- 2152, Olympus - E-5 - 16bit (4:3).ORF, `ab0d54e3819c9372df0fa98c8686dba0ae87c9d43526a5dd6fd26bd2a664483d`
- 2430, Olympus - E-P2 - 16bit (4:3).ORF, `2666a6ed03e8678bc6ce0e5354f39a07284e6f8b200dc696d9b543dc9f82bdd5`
- 2431, Olympus - XZ-10 - 12bit (4:3).ORF, `a25383acad9b5bb0bb404715e0957f2eb80aa1aaad6c448a71025c03cfa631be`
- 2533, Olympus - E-PL9 - 16bit (4:3).ORF, `22525e54442f52281d007b5e8a75a2c61f768856699cf5ed697d85e055f2cc4f`
- 2602, OLYMPUS - STYLUS1,1s - 16bit (4:3).ORF, `09ffeb7d6741e877cb4102c7a379a896d6c1c178cff8844013f7960f03f1234f`
- 2856, Olympus - E-M5 Mark II - 16bit 16bit "high-res" (4:3).ORF, `5c42fa75d6b549514b722e2c50726c03e34fac4909ec3640e147ea7fa825fc8d`
- 2857, Olympus - E-M5 Mark II - 16bit 16bit "normal" (4:3).ORI, `f2c7a1dfbfcc6093b28373a1616569b8bd9c2d91cb708480b8312d510c57fbd6`
- 2977, Olympus - PEN-F - 16bit (4:3).orf, `f87a5f3295aeb4d6ab27bb5b41c5e0f3a211ec9b4e3b1d9f105a650bee1a2f13`
- 2978, Olympus - PEN-F - 16bit (4:3).orf, `156bf12075c4f69a3e475518f67db9d4010972d8123bdd27ae8c9177b443c374`
- 3041, Olympus - E-M1X - 16bit (4:3).ORF, `ab171cedfe3a65438dd47c2df704a7d3001f45f5ab43e67b7f96cfe30b6ebbcf`
- 3210, Olympus - TG-6 - 16bit (4:3).ORF, `edd6f928bc790c79852a17fce56718d26563c7a593894d22970ef0fdb86ba45f`
- 3331, Olympus - Stylus1 - 16bit (4:3).ORF, `cc2ad0341b2dcebdda8e5365e3ff96086180f24cd1ffe3401e7903b54ad54091`
- 3540, Olympus - E-500 - 16bit (4:3).ORF, `fa5a4759b2de2b573f59629ad1baf64ad04a85fb8fe1fb3cbf68e08a42fff4f0`
- 3573, Olympus - E-M5 Mark III - 16bit (4:3).ORF, `391f2f6ba712a517212cae53bfc9a313fc4d106d0b04d3b9af68a4ed2d5d944e`
- 3588, OLYMPUS - E-M5 Mark III - 16bit (4:3).ORF, `24de6ac3bd5e668ee22fd0dbf2e344608949eb85f7342f28470ce709c9d51226`
- 3624, Olympus - E-330 - 16bit (4:3).ORF, `ba11eb970ab32e1e9cf3d0176041e4bd11c501d445720c0a344217e785ad65a6`
- 3800, Olympus - E-M1MarkIII - 16bit (4:3).ORF, `1e7a256eff14df75055dd7fe7a68aabefb4d8ed475317e80ebf7ff77d5bcfd3f`
- 3801, Olympus - E-M1MarkIII - 16bit (4:3).ORF, `e9a21175493e9d9e5653aa91f1bd6fbf421aba42b59b4ffe7cd1f7cac2de385c`
- 3802, Olympus - E-M1MarkIII - 16bit (4:3).ORI, `83932e61123a90a423a81f87d08c9ed66bca5feb0d900d7d1d0924845dfa9f46`
- 3803, Olympus - E-M1MarkIII - 16bit (4:3).ORF, `4ad47518e3766fae6b98f8b18f3aae3c277e5966028e3f2e0d2702bb0f17a3cd`
- 3804, Olympus - E-M1MarkIII - 16bit (4:3).ORI, `d831692b608471ad64667eb2485bab553de0ddb9366d384c4ecb731092b5dc42`
- 3970, Olympus - E-PL10 - 16bit (4:3).ORF, `6911f11810545cc2c55882ef6fa6aa2f25d34674865f8ade15e47990865e37ed`
- 4126, Olympus - E-M10 Mark IV - 16bit (4:3).ORF, `ce03e936cb2e8131343e7045a3249f78477bd2ae944e121ace72058b89fef509`
- 4132, Olympus - E-M10 Mark IV - 16bit (4:3).ORF, `77b67d898f85d3d738cb16daf9740c0fcf078ce9662c381994604ac540ce36b4`
- 4927, Olympus - E-M10 Mark IIIs - 16bit (4:3).ORF, `8bc0009eaacdbeacc72606581665702a1242bc6d4b405d1f0b3f149fe6c85e55`
- 5099, Olympus - E-P1 - 16bit (4:3).ORF, `862b9d409279af0528810aa02eb5b4140d7854f9d637d4188b82ebaf4bf0d4cf`
- 5283, OM System - OM-1 - 16bit (4:3).ORF, `bf2eef6becc0851e48231617c3e2eac27a2cdb44c75b93035c561d837952c18b`
- 5284, OM System - OM-1 - 16bit (4:3).ORF, `f0301e1b49a4ffbb366ec9800ebe9210f421fb25e75dcdf7d63e4b05bc063caf`
- 5285, OM System - OM-1 - 16bit (4:3).ORF, `862dda54644400335633578ea3a37912fbe56429f755499fdbcab9e993543874`
- 5286, OM System - OM-1 - 16bit (4:3).ORI, `2fd8bd46e2644fe28092fd921d9647007afd6d1e879c5ff19b1e3df50c578df1`
- 5287, OM System - OM-1 - 16bit (4:3).ORI, `dcbc06ba28c641197b65d931c203c5dd697fd34ae79b649a9a6d9cfc84e4bca2`
- 5449, Olympus - E-510 - 16bit (4:3).ORF, `efab3d91a4f52ce65a428c15af5a54a170ef5961fb7765265c432faf19d6744c`
- 5782, Olympus - E-450 - 16bit (4:3).ORF, `ce44576886d214d194896c32bdd05881f25a23053455decc3da18c46fee96fad`
- 5915, Olympus - E-M10 Mark II - 16bit (4:3).ORF, `1a95224502963c892aa69ceb58767e58730f223c4b60b62119261d45eeba8bd9`
- 5980, Olympus - E-P7 - 16bit (4:3).ORF, `391b7a28d088f093a93d05c43b82bc8e9403579dea8cdc066d28af53a773d9c5`
- 6343, OM System - OM-5 - 16bit (4:3).ORF, `ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7`
- 6344, OM System - OM-5 - 16bit (4:3).ORF, `42b13fbc10627907881975fb1f617bd7afa90ef448c239ce3ad41a4b9ceca512`
- 6345, OM System - OM-5 - 16bit (4:3).ORI, `c8277d133c7ac86c7e4af5787fa06515fef8fe044c1b22209c62704537c48e02`
- 6346, OM System - OM-5 - 16bit (4:3).ORF, `ffd47d5924b65abdd8af761665d67705fe028cfd08e5efbc264b64a20830d9f4`
- 6347, OM System - OM-5 - 16bit (4:3).ORI, `062c4934ae9ab7595a45b56e2ad36a5ca05d75a8bed64f6d18cc88f9006ac9a9`
- 6946, OM System - TG-7 - 16bit (4:3).ORF, `4f7344c67bfcfcfec45f754195ba612fc2ad6312f5fab87812bf04b9e9e7d46a`
- 7262, OM System - OM-1 Mark II - 16bit (4:3).orf, `d0fe58daf2f0bd749ecb18311e55408f0e7804de8e5e6580e815eae50d834cbd`
- 7263, OM System - OM-1 Mark II - 16bit (4:3).orf, `780fa6a22ecd272cf3e86c04114439953b95fbc1bba8a05b4c99595a22e36bba`
- 7264, OM System - OM-1 Mark II - 16bit (4:3).ori, `d7fea34029b9926e7d9cf6ecdfef9de90cbda41ff6eea009cc1a4f5b1813b8df`
- 7265, OM System - OM-1 Mark II - 16bit (4:3).orf, `c7bd43b29ed89542058534b867fa894b8550d1960503cf4b4cb9f5912fd242b3`
- 7266, OM System - OM-1 Mark II - 16bit (4:3).ori, `1c994e4bf5aa4e48d6ec97a1f83558184a866f71bca2b5b1bf914a159927e199`
- 7267, OM System - OM-1 Mark II - 16bit (4:3).orf, `5c4845bcf87d868c1b770d7e92e574e148d82acb2806cddd9df5a7a47d7cd756`
- 7268, OM System - OM-1 Mark II - 16bit (4:3).ori, `a5ee1e874d7aa357192173e12695627f90a8800a272b6c6e4959f029afb59837`
- 7269, OM System - OM-1 Mark II - 16bit (4:3).orf, `dd2a6c1c4ca4d86201207925477e2ea8e50ebd53d7df9117847093f5023540ec`
- 7270, OM System - OM-1 Mark II - 16bit (4:3).ori, `e4f3583f0bfb1efb0f40b201c5bb0cb1c30ace875a7f96d93fa7dddcc6966f5f`
- 7796, OM System - OM-3 - 16bit (4:3).ORF, `1cee7deb661e45101ab3ca6c4240d24ed949b167ed423703fca15c09dd8ec176`
- 7797, OM System - OM-3 - 16bit (4:3).ORF, `318e35647d93b2c598c0fec1d0d075336d2e2f5e6930faee05f32182c9a8ac5f`
- 7798, OM System - OM-3 - 16bit (4:3).ORI, `6fab41a21d5c8c0469619049888b0a36c7b260d893e3c35c174044b7293e9d43`
- 7799, OM System - OM-3 - 16bit (4:3).ORF, `9da7407d27007320c5bcf4e4d0b8c5c7bb533669cf4fabdf4e6a4b567cf318cc`
- 7800, OM System - OM-3 - 16bit (4:3).ORI, `5640fb1a2ceff83d3678f46a7acdabd9ec393d318718c9c48a9c650afe7a7c58`
- 7801, OM System - OM-3 - 16bit (4:3).ORF, `8832599870d20a96f28897e3e28d9705a4bd05871c9833c7c60a8b59d7d64b82`
- 7802, OM System - OM-3 - 16bit (4:3).ORI, `2f8c0363376fe1c4f669f1c6c881611e8a71e39320bbac3c691405583b671cf2`
- 7803, OM System - OM-3 - 16bit (4:3).ORF, `63a5b4da41fdbe8b31213ca7a11408dfd0453d893f17ac09a73471580ffbd8f0`
- 7804, OM System - OM-3 - 16bit (4:3).ORI, `bcc05bd57e78cbbb308a596f97987975f7167b17768d8c2d536c87e0c34298e0`
- 8549, OM System - OM-5 Mark II - 16bit (4:3).ORF, `c6fe861982ddc18464cf6858d2700f6813cc3a17956bcb12d1179212c999c76a`
- 8550, OM System - OM-5 Mark II - 16bit (4:3).ORI, `8ebb09fb177f29f88faab15a1b1498182448a4b6d65dc5a2f533d5d5b5de1be0`
- 8552, OM System - OM-5 Mark II - 16bit (4:3).ORF, `4d79adadf1f736cdbd666bc5f750ee75235b365ecb5fa8dcbc6cd7ca461343ed`
- 8553, OM System - OM-5 Mark II - 16bit (4:3).ORF, `6c34d583e2c98840828fa500e54e47f270f138dfc697a9a7cd084575305d3c9f`
- 8554, OM System - OM-5 Mark II - 16bit (4:3).ORI, `de530604f60a7e4f867ff8bf7889fc8b49fbe3e93f660ba72d13dccabe5bc583`

The ten attempted public CC0 files with no supported baseline preview:

- 780, Olympus - C7070WZ - 12bit (4:3).ORF, `9d55506f9d6ee31d2d4c4b6df0dcd1d016d358b3e5eb4ed31edd7227dfefd5f8`
- 792, Olympus - SH-2 - 12bit (4:3).ORF, `6e6b9b7dd9ded7c4b364b83116c817ca2d6daac15f2e9ef7796159b08c3288a1`
- 1799, Olympus - C5060WZ - 12bit (4:3).ORF, `3fc12bc3f6320cfab456111d7805b446e329fdd1907680be55e2e163e5e084bd`
- 1800, Olympus - E-1 - 16bit (4:3).ORF, `042286653fbae5b085bef4a4e626145385ea6e82e817f166b4904abcef64457c`
- 2420, Olympus - SP510UZ - 12bit (4:3).ORF, `f0737d78bb2e588963a3d5038fab493cdff1c9c48475704de96d797bbb81e62a`
- 2878, Olympus - E-300 - 16bit (4:3).ORF, `6d818dbff78b3e2efa4835f568d04733052b9211e6bc65b0a3748a841170e95b`
- 3438, Olympus - SP565UZ - 12bit (4:3).ORF, `5088771f83ce08a001b44672e1dd9f013e603933c37ce1bfb7030a02abbe801c`
- 5424, Olympus - E-10 - 16bit (4:3).ORF, `2bfdade72439017a60a47aad1e5bbcb1aca36f2be7a21e94a4257a678fb6f4da`
- 5491, Olympus - SP570UZ - 12bit (4:3).ORF, `baab92391834076b427e406e98da79aaba48fb87243d6ccae60e08e299cfccf7`
- 8609, Olympus - SP550UZ - 12bit (4:3).ORF, `05f49918e1b1894c3abd2b5451b356f7a00adb1c8568abc5babff33fcade1bb2`

## Verification

New run started on 2026-10-22 at 02:14 UTC, after the lead was posted at
02:00:46 UTC and after the claim at 02:13:11 UTC. Python 3.13.15, Windows.
All 104 local SHA-256 values matched the retained verified-CC0 inventory
(104 checked, 0 missing, 0 mismatched); `samples/manifest.csv` hashed to
`535d99ace97e3424d561ef1ed35cb8003c3cad3fd827c31ee0ac82d96d66db32`, the
inventory's recorded reference, and every input had an existing manifest
row. No download, catalogue request or manifest edit was made. No image or
preview was rendered or viewed, and only aggregate pair scores were printed.

Self-verification: this account is also the lead's finder and no separate
human account was available, so this is not independent human verification.
The lead already used every usable CC0 file of the cohort, so no unused
usable file exists. The wider 104-file attempted cohort is the additional
new body of evidence: the tool classified exactly 94 files as ok and the
same ten older bodies as unsupported, then produced 4371 eligible pairs and
110 positives over the 5356 total pairs (the extra 985 pairs are the ones
with at least one unsupported input).

The tool's own controls pass: `tools/test_preview_pair_screen.py` ran 6
tests OK and `tools/test_jpeg_dc.py` ran 4 tests OK.

Exact 94-file run, using the lead's command and count script:

```
pairs 4371 positive 110 same_model_positive 110 cross_model_positive 0
cross_model_max 0.89809576563252
positive_min 0.9935009635229081 positive_max 0.9999981079624815
```

The tool summary line was `samples 94`, `pairs 4371`, `eligible_pairs
4371`, `screen_positive 110`, `grid 12`, `threshold 0.98`,
`alignment identity_only`. The same-model median was 0.99943878614918025.
Per-model positive/total pair counts also match the lead: E-M1 Mark II
10/15, E-M1 Mark III 2/10, E-M5 Mark II 1/1, E-M5 Mark III 0/1, E-M10 Mark
IV 0/1, OM-1 4/10, OM-1 Mark II 36/36, OM-3 36/36, OM-5 10/10, OM-5 Mark
II 10/10, PEN-F 1/1. All 94 previews were 3200x2400 (86) or 1600x1200
(8), and no file was rejected as low-information (12x12 grid SD 4.9321 to
359.0301).

Grid-resolution check. The same 94 previews were binned at 24x24 and 32x32
with the same complete-block and prefix-partition rule. The positive set is
identical to the 12x12 set at both resolutions (110 of 110, no extra pair),
and all 110 remain same-model with 0 cross-model positives:

- 24x24: cross-model maximum 0.8662213750806403, positive minimum
  0.9904320146500482, positive maximum 0.9999957457406183.
- 32x32: cross-model maximum 0.8571097621640811, positive minimum
  0.9862224835926673, positive maximum 0.9999939483169507.

GPU cross-check (supporting only, not part of the reproduction path). An
RTX 3090 with CuPy 14.0.1 recomputed the 12x12, 24x24 and 32x32 matrices in
float64 from independently binned grids. Against the public CPU tool's
printed 12x12 pair scores the maximum absolute difference was
8.881784197001252e-16; against a numpy CPU matrix it was at most
1.887379141862766e-15; an independent Pearson-formula spot-check of four
pairs agreed to 2.220446049250313e-16. A 100,000-replicate null that
independently permutes each 12x12 grid and takes the maximum |r| over the
4371 pairs gave p99 |r| 0.38365 in 2.72 s, close to the lead's supporting
0.38374; its maximum differed (0.48827 versus 0.46801), consistent with a
different extreme-tail draw. The null is not a false-positive calibration
and no count above depends on it.

Limitations: same-model means identical `model` text in
`samples/manifest.csv`, not a body census; the pool has no scene or capture
labels and almost no cross-model same-session pairs; 0.98 is a fixed
screening cutoff; the 86 3200x2400 and 8 1600x1200 previews were not
separated; and this is a self-verification, not independent human
verification.

## Reproduce

Use `tools/preview_pair_screen.py` and `tools/jpeg_dc.py` from `main` at
`2a09ce78d33d7c93e394ae4477f3c713dad86f92` (or the pinned commit above; the
blobs are identical). Download the 94 public CC0 ids listed above with
`tools/pixls_samples.py`, then pass their local paths explicitly:

```
python -I -B tools/test_preview_pair_screen.py
python -I -B tools/test_jpeg_dc.py
python -I -B tools/preview_pair_screen.py <the 94 paths> > pairs.jsonl
```

Save this one-off count script as `count_pairs.py` and run it from the repo
root:

```python
import csv
import json
import sys

model = {r["sha256"]: r["model"] for r in csv.DictReader(open("samples/manifest.csv", encoding="utf-8", newline=""))}
rows = [json.loads(line) for line in open(sys.argv[1], encoding="utf-8") if line.strip()]
pairs = [r for r in rows if "pair" in r]
pos = [r for r in pairs if r["screen_positive"]]
same = sum(model[r["pair"][0]] == model[r["pair"][1]] for r in pos)
cross = [r for r in pairs if model[r["pair"][0]] != model[r["pair"][1]]]
print("pairs", len(pairs), "positive", len(pos), "same_model_positive", same, "cross_model_positive", len(pos) - same)
print("cross_model_max", max(r["r"] for r in cross))
print("positive_min", min(r["r"] for r in pos), "positive_max", max(r["r"] for r in pos))
```

```
python -I -B count_pairs.py pairs.jsonl
```

Expected: `pairs 4371 positive 110 same_model_positive 110
cross_model_positive 0`; `cross_model_max` approximately 0.8980957656;
`positive_min` 0.9935009635229081 and `positive_max` 0.9999981079624815.
For the 104-file attempted cohort, pass all 104 paths instead: the tool
summary is `samples 104`, `pairs 5356`, `eligible_pairs 4371`,
`screen_positive 110`, with ten unsupported samples. For the 24x24 and
32x32 checks, copy the screen to a scratch path and change only `GRID` to
24 or 32; the other settings stay frozen.
