# The compression tag is 1 on every ORF; payload size and bits per sample separate the classes

Author: @radialmonster
Verified by: @radialmonster
Lead: #10
Variant: container
Builds on: #28

## Claim
On every CC0 Olympus / OM System ORF and ORI file on raw.pixls.us, the raw IFD's TIFF Compression tag (0x103) is 1 ("uncompressed"), whether the payload is compressed or not, so the tag cannot be used to classify. In the current set (104 files, 63 model spellings in the files' own tags):
- Compression tag: 1 on all 104 files.
- BitsPerSample: 16 on all 87 compressed (`variable`) files; also 16 on the 8 packed-12.8 and packed-16 files; 12 on the 9 packed-12 files.
- Bits per pixel (payload bytes x 8 / pixels) separates the classes: the 87 compressed files lie between 6.021 and 8.794 bpp; the fixed packings are exactly 12, 12.8 and 16.000 (E-1 is 16.000, as in the lead).
- One correction to the lead's "about 6-8.5": 86 of the 87 compressed files are at or below 8.5, but OM-1MarkII file 7269 (8172 wide High Res Shot) is 8.794. (OM-1MarkII 7267, 8.450, and OM-3 7803, 8.446, are just under.)
- High Res Shot-sized payloads (over 6000 wide) are in the same container with the same tag value: 21 files, of which 19 are compressed (6.0 to 8.8 bpp) and 2 are packed-12.8 (E-M5MarkII 2856, PEN-F 2977).

## Original evidence
Lead #10 by @radialmonster (2026-10-18): `tools/orf_signature.py` (last changed in 67a763c at the time) on 17 CC0 files from E-P7, E-M1MarkII, E-M5, E-1, OM-1, OM-3 and OM-5MarkII. The lead did not record file ids.

## Verification
Self-verification by @radialmonster, a new run on 2026-10-19 after the lead was posted (HEAD 72c77df, `tools/orf_signature.py` last changed in 62c368a, Python 3.13.15). All 104 CC0 Olympus / OM files from `pixls_samples.py list` were used (downloaded earlier by the same tool, SHA-256 verified then; `pixls_samples.py check` was run again on all 104 here: 104 CC0, 0 other). The lead recorded no file ids, so I cannot say which files it used; the run covers 48 compressed models, 42 of them bodies the lead does not name (the lead names E-P7, E-M1MarkII, E-M5, OM-1, OM-3 and OM-5MarkII among the compressed ones). The tag reads 1 on every compressed file, so the lead's claim holds on all of them.
- Tag 1 on 104/104; bits per sample 16 on 87/87 compressed, 12 on 9/9 packed-12.
- Compressed bpp: min 6.021 (E-M1MarkII 1994), max 8.794 (OM-1MarkII 7269); only that one exceeds 8.5.
- Magic: ORF-RO on 98 files, ORF-RS on 6; the tag is 1 in both.

Every file (raw.pixls.us id, model, payload size, bpp, class, bits per sample, tag, SHA-256):

- 241 E-P3 4080x3040, 6.725 bpp, variable, bits/sample 16, tag 1, `540edabdd9d4e6ef8602f56443730cc3133d714dc4d3d2c607e2f0aa6be5cbcd`
- 780 C7070WZ 3088x2309, 12.000 bpp, packed-12, bits/sample 12, tag 1, `9d55506f9d6ee31d2d4c4b6df0dcd1d016d358b3e5eb4ed31edd7227dfefd5f8`
- 792 SH-2 4624x3470, 12.000 bpp, packed-12, bits/sample 12, tag 1, `6e6b9b7dd9ded7c4b364b83116c817ca2d6daac15f2e9ef7796159b08c3288a1`
- 1051 E-M1 4640x3472, 6.912 bpp, variable, bits/sample 16, tag 1, `19ba17e778ae802d4039f0e88bb1cd68825780788b8058c479067e32b9a63eda`
- 1079 E-PM1 4080x3040, 6.790 bpp, variable, bits/sample 16, tag 1, `db8a564def35efaadf72cf74de92fa3959b2ab44bee4e0ec7876305830c59765`
- 1084 E-M5 4640x3472, 6.619 bpp, variable, bits/sample 16, tag 1, `b2221977cbc6eba0d3b363351072092e5647eaa0d02a5d8432b5d985b29f669f`
- 1090 E-P5 4640x3472, 6.157 bpp, variable, bits/sample 16, tag 1, `a1345ebe8d8722e791cbd52778e73257c5ff457ee13988fd78eac61eec841c21`
- 1135 TG-4 4640x3472, 7.702 bpp, variable, bits/sample 16, tag 1, `a056d3fad56762d8a125806a0a4857341f115bc6303085b7297758be8d93b20a`
- 1173 E-410 3720x2800, 7.399 bpp, variable, bits/sample 16, tag 1, `b545f3d831275d7febb1d02bfa22b03078eeff27fcb4c5be6806e89857bb1ed7`
- 1233 E-PM2 4640x3472, 6.878 bpp, variable, bits/sample 16, tag 1, `84f9442e59eba80a6272a07759517dd0e32dfa114d2cc541ec3a67eea34cca55`
- 1330 E-PL3 4080x3040, 7.547 bpp, variable, bits/sample 16, tag 1, `ce90f016fc6ddb14e407071c5a035b68039c5aec5a801e4152a88d2c2388f0d4`
- 1331 E-M10 4640x3472, 6.849 bpp, variable, bits/sample 16, tag 1, `d7f6ac99ee1f824e81ec0e71599f0f87f9b2e2675f7ddfdb21202281b8bdc5e0`
- 1430 E-PL6 4640x3472, 6.652 bpp, variable, bits/sample 16, tag 1, `38d3750abbcf847bba58e254b2ab8c57d8c9f3fc48490c29ae2b55c4e84d5f64`
- 1431 E-PL7 4640x3472, 7.151 bpp, variable, bits/sample 16, tag 1, `e0e138e9d33b0d2a16c0a9378582ddaac71d0b2cf07bc9ed459df275aa025c60`
- 1432 XZ-2 3984x2986, 12.000 bpp, packed-12, bits/sample 12, tag 1, `675fefe7c9e99281783b987889d723b5f46692f5c20e19fed5e422c7c6d2636b`
- 1723 TG-5 4040x3016, 7.465 bpp, variable, bits/sample 16, tag 1, `1fd6d09b8c93a9bb629e1871859c18a6763397301396844c34217330de094453`
- 1752 E-PL8 4640x3472, 6.331 bpp, variable, bits/sample 16, tag 1, `68400f859dea4be9a398fdc1f97613962b92d14b53d96531e2310b7dde2e674e`
- 1754 E-PL1 4100x3084, 7.931 bpp, variable, bits/sample 16, tag 1, `d8895526c8215925468d503d1879b18c2e3e38140bffeba77351b9e55683aac9`
- 1759 XZ-1 3680x2760, 7.351 bpp, variable, bits/sample 16, tag 1, `3f5fb6f36ad4132323cab790e30b0bc10217aa7fb703518005a5800c908ba8a3`
- 1776 E-PL5 4640x3472, 6.529 bpp, variable, bits/sample 16, tag 1, `08e90f890283f4af3c05b14c67851dd2d52c5fcaf24522634d0d9ef734213427`
- 1787 E-M10 Mark III 4640x3472, 8.333 bpp, variable, bits/sample 16, tag 1, `11d90cbb564ad2c660c7a8d5d81d99c2c018aa27fdec45ed6c461fa5d24f942b`
- 1788 E-PL2 4100x3084, 6.903 bpp, variable, bits/sample 16, tag 1, `85055c7c661f96ba1c930fdd522d0598c9bc44ea6363725e9cd48646d8782f4e`
- 1799 C5060WZ 2608x1949, 12.000 bpp, packed-12, bits/sample 12, tag 1, `3fc12bc3f6320cfab456111d7805b446e329fdd1907680be55e2e163e5e084bd`
- 1800 E-1 2624x1966, 16.000 bpp, packed-16, bits/sample 16, tag 1, `042286653fbae5b085bef4a4e626145385ea6e82e817f166b4904abcef64457c`
- 1803 E-3 3720x2800, 6.920 bpp, variable, bits/sample 16, tag 1, `ba4605bbd9fe9b77971da444bcdb1698904c0ad4ebdf9dd42dd45ab255f3f6d4`
- 1805 E-620 4100x3084, 6.820 bpp, variable, bits/sample 16, tag 1, `b3aff4240fc5b3f772c58f2b651c9d47904a575d5a22fcac49ed43374a5d779a`
- 1993 E-M1MarkII 5240x3912, 6.151 bpp, variable, bits/sample 16, tag 1, `0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8`
- 1994 E-M1MarkII 10400x7792, 6.021 bpp, variable, bits/sample 16, tag 1, `f8d04ca777b3cd4d1eed4c2971d713d6ac7397bf1254929b4097c4b619f49c23`
- 1995 E-M1MarkII 5240x3912, 6.154 bpp, variable, bits/sample 16, tag 1, `8af918366ed969c6dddf5a48b8810fec1024858d22c75c5f1ac1a5c750a57a1f`
- 1996 E-M1MarkII 10400x7792, 6.022 bpp, variable, bits/sample 16, tag 1, `eeb589558062114c1f4db00c2341eac6741fb345be871a40f3428600f84a95a2`
- 1997 E-M1MarkII 5240x3912, 6.154 bpp, variable, bits/sample 16, tag 1, `89138ccc958509ca1beb7028452400ab7f42061c0fc56e35c8a7d7a4a808dd0a`
- 1998 E-M1MarkII 5240x3912, 6.156 bpp, variable, bits/sample 16, tag 1, `4bc52d99e4fbf2f09335a3301a4634bc261a98441edb824434ec069f7026cd71`
- 2150 E-420 3720x2800, 7.250 bpp, variable, bits/sample 16, tag 1, `4b981b6e82357514b00183f3c676202625a61684373cc32decb361639ed2eec4`
- 2151 E-400 3768x2840, 16.000 bpp, packed-16, bits/sample 16, tag 1, `1354e0ac98ea90820227650031d8215637a2aaabd15de995c5a1e00b1986261b`
- 2152 E-5 4100x3084, 6.828 bpp, variable, bits/sample 16, tag 1, `ab0d54e3819c9372df0fa98c8686dba0ae87c9d43526a5dd6fd26bd2a664483d`
- 2420 SP510UZ 3088x2309, 12.000 bpp, packed-12, bits/sample 12, tag 1, `f0737d78bb2e588963a3d5038fab493cdff1c9c48475704de96d797bbb81e62a`
- 2430 E-P2 4100x3084, 8.059 bpp, variable, bits/sample 16, tag 1, `2666a6ed03e8678bc6ce0e5354f39a07284e6f8b200dc696d9b543dc9f82bdd5`
- 2431 XZ-10 3984x2990, 12.000 bpp, packed-12, bits/sample 12, tag 1, `a25383acad9b5bb0bb404715e0957f2eb80aa1aaad6c448a71025c03cfa631be`
- 2533 E-PL9 4640x3472, 6.980 bpp, variable, bits/sample 16, tag 1, `22525e54442f52281d007b5e8a75a2c61f768856699cf5ed697d85e055f2cc4f`
- 2602 STYLUS1,1s 4000x2992, 6.630 bpp, variable, bits/sample 16, tag 1, `09ffeb7d6741e877cb4102c7a379a896d6c1c178cff8844013f7960f03f1234f`
- 2856 E-M5MarkII 9280x6932, 12.800 bpp, packed-12.8, bits/sample 16, tag 1, `5c42fa75d6b549514b722e2c50726c03e34fac4909ec3640e147ea7fa825fc8d`
- 2857 E-M5MarkII 4640x3472, 6.529 bpp, variable, bits/sample 16, tag 1, `f2c7a1dfbfcc6093b28373a1616569b8bd9c2d91cb708480b8312d510c57fbd6`
- 2878 E-300 3360x2504, 12.800 bpp, packed-12.8, bits/sample 16, tag 1, `6d818dbff78b3e2efa4835f568d04733052b9211e6bc65b0a3748a841170e95b`
- 2977 PEN-F 10400x7796, 12.800 bpp, packed-12.8, bits/sample 16, tag 1, `f87a5f3295aeb4d6ab27bb5b41c5e0f3a211ec9b4e3b1d9f105a650bee1a2f13`
- 2978 PEN-F 5200x3904, 6.761 bpp, variable, bits/sample 16, tag 1, `156bf12075c4f69a3e475518f67db9d4010972d8123bdd27ae8c9177b443c374`
- 3041 E-M1X 5240x3912, 7.193 bpp, variable, bits/sample 16, tag 1, `ab171cedfe3a65438dd47c2df704a7d3001f45f5ab43e67b7f96cfe30b6ebbcf`
- 3210 TG-6 4040x3016, 7.877 bpp, variable, bits/sample 16, tag 1, `edd6f928bc790c79852a17fce56718d26563c7a593894d22970ef0fdb86ba45f`
- 3331 STYLUS1 4000x2992, 6.641 bpp, variable, bits/sample 16, tag 1, `cc2ad0341b2dcebdda8e5365e3ff96086180f24cd1ffe3401e7903b54ad54091`
- 3438 SP565UZ 3664x2741, 12.000 bpp, packed-12, bits/sample 12, tag 1, `5088771f83ce08a001b44672e1dd9f013e603933c37ce1bfb7030a02abbe801c`
- 3540 E-500 3360x2504, 12.800 bpp, packed-12.8, bits/sample 16, tag 1, `fa5a4759b2de2b573f59629ad1baf64ad04a85fb8fe1fb3cbf68e08a42fff4f0`
- 3573 E-M5MarkIII 10400x7792, 6.479 bpp, variable, bits/sample 16, tag 1, `391f2f6ba712a517212cae53bfc9a313fc4d106d0b04d3b9af68a4ed2d5d944e`
- 3588 E-M5MarkIII 5240x3912, 6.353 bpp, variable, bits/sample 16, tag 1, `24de6ac3bd5e668ee22fd0dbf2e344608949eb85f7342f28470ce709c9d51226`
- 3624 E-330 3280x2450, 12.800 bpp, packed-12.8, bits/sample 16, tag 1, `ba11eb970ab32e1e9cf3d0176041e4bd11c501d445720c0a344217e785ad65a6`
- 3800 E-M1MarkIII 5240x3912, 6.425 bpp, variable, bits/sample 16, tag 1, `1e7a256eff14df75055dd7fe7a68aabefb4d8ed475317e80ebf7ff77d5bcfd3f`
- 3801 E-M1MarkIII 8200x6132, 6.033 bpp, variable, bits/sample 16, tag 1, `e9a21175493e9d9e5653aa91f1bd6fbf421aba42b59b4ffe7cd1f7cac2de385c`
- 3802 E-M1MarkIII 5240x3912, 6.395 bpp, variable, bits/sample 16, tag 1, `83932e61123a90a423a81f87d08c9ed66bca5feb0d900d7d1d0924845dfa9f46`
- 3803 E-M1MarkIII 10400x7792, 6.112 bpp, variable, bits/sample 16, tag 1, `4ad47518e3766fae6b98f8b18f3aae3c277e5966028e3f2e0d2702bb0f17a3cd`
- 3804 E-M1MarkIII 5240x3912, 6.712 bpp, variable, bits/sample 16, tag 1, `d831692b608471ad64667eb2485bab553de0ddb9366d384c4ecb731092b5dc42`
- 3970 E-PL10 4640x3472, 7.562 bpp, variable, bits/sample 16, tag 1, `6911f11810545cc2c55882ef6fa6aa2f25d34674865f8ade15e47990865e37ed`
- 4126 E-M10MarkIV 5200x3904, 6.792 bpp, variable, bits/sample 16, tag 1, `ce03e936cb2e8131343e7045a3249f78477bd2ae944e121ace72058b89fef509`
- 4132 E-M10MarkIV 5200x3904, 6.474 bpp, variable, bits/sample 16, tag 1, `77b67d898f85d3d738cb16daf9740c0fcf078ce9662c381994604ac540ce36b4`
- 4927 E-M10MarkIIIS 4640x3472, 7.490 bpp, variable, bits/sample 16, tag 1, `8bc0009eaacdbeacc72606581665702a1242bc6d4b405d1f0b3f149fe6c85e55`
- 5099 E-P1 4100x3084, 7.218 bpp, variable, bits/sample 16, tag 1, `862b9d409279af0528810aa02eb5b4140d7854f9d637d4188b82ebaf4bf0d4cf`
- 5283 OM-1 5220x3912, 7.836 bpp, variable, bits/sample 16, tag 1, `bf2eef6becc0851e48231617c3e2eac27a2cdb44c75b93035c561d837952c18b`
- 5284 OM-1 8180x6132, 6.947 bpp, variable, bits/sample 16, tag 1, `f0301e1b49a4ffbb366ec9800ebe9210f421fb25e75dcdf7d63e4b05bc063caf`
- 5285 OM-1 10400x7792, 6.283 bpp, variable, bits/sample 16, tag 1, `862dda54644400335633578ea3a37912fbe56429f755499fdbcab9e993543874`
- 5286 OM-1 5220x3912, 7.813 bpp, variable, bits/sample 16, tag 1, `2fd8bd46e2644fe28092fd921d9647007afd6d1e879c5ff19b1e3df50c578df1`
- 5287 OM-1 5220x3912, 7.538 bpp, variable, bits/sample 16, tag 1, `dcbc06ba28c641197b65d931c203c5dd697fd34ae79b649a9a6d9cfc84e4bca2`
- 5424 E-10 2256x1684, 16.000 bpp, packed-16, bits/sample 16, tag 1, `2bfdade72439017a60a47aad1e5bbcb1aca36f2be7a21e94a4257a678fb6f4da`
- 5449 E-510 3720x2800, 7.819 bpp, variable, bits/sample 16, tag 1, `efab3d91a4f52ce65a428c15af5a54a170ef5961fb7765265c432faf19d6744c`
- 5491 SP570UZ 3664x2741, 12.000 bpp, packed-12, bits/sample 12, tag 1, `baab92391834076b427e406e98da79aaba48fb87243d6ccae60e08e299cfccf7`
- 5782 E-450 3720x2800, 6.983 bpp, variable, bits/sample 16, tag 1, `ce44576886d214d194896c32bdd05881f25a23053455decc3da18c46fee96fad`
- 5915 E-M10MarkII 4640x3472, 6.846 bpp, variable, bits/sample 16, tag 1, `1a95224502963c892aa69ceb58767e58730f223c4b60b62119261d45eeba8bd9`
- 5980 E-P7 5200x3904, 6.440 bpp, variable, bits/sample 16, tag 1, `391b7a28d088f093a93d05c43b82bc8e9403579dea8cdc066d28af53a773d9c5`
- 6343 OM-5 5240x3912, 6.936 bpp, variable, bits/sample 16, tag 1, `ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7`
- 6344 OM-5 8200x6132, 6.494 bpp, variable, bits/sample 16, tag 1, `42b13fbc10627907881975fb1f617bd7afa90ef448c239ce3ad41a4b9ceca512`
- 6345 OM-5 5240x3912, 7.149 bpp, variable, bits/sample 16, tag 1, `c8277d133c7ac86c7e4af5787fa06515fef8fe044c1b22209c62704537c48e02`
- 6346 OM-5 10400x7792, 6.445 bpp, variable, bits/sample 16, tag 1, `ffd47d5924b65abdd8af761665d67705fe028cfd08e5efbc264b64a20830d9f4`
- 6347 OM-5 5240x3912, 7.173 bpp, variable, bits/sample 16, tag 1, `062c4934ae9ab7595a45b56e2ad36a5ca05d75a8bed64f6d18cc88f9006ac9a9`
- 6946 TG-7 4040x3016, 8.076 bpp, variable, bits/sample 16, tag 1, `4f7344c67bfcfcfec45f754195ba612fc2ad6312f5fab87812bf04b9e9e7d46a`
- 7262 OM-1MarkII 5220x3912, 8.078 bpp, variable, bits/sample 16, tag 1, `d0fe58daf2f0bd749ecb18311e55408f0e7804de8e5e6580e815eae50d834cbd`
- 7263 OM-1MarkII 8180x6132, 7.191 bpp, variable, bits/sample 16, tag 1, `780fa6a22ecd272cf3e86c04114439953b95fbc1bba8a05b4c99595a22e36bba`
- 7264 OM-1MarkII 5220x3912, 8.107 bpp, variable, bits/sample 16, tag 1, `d7fea34029b9926e7d9cf6ecdfef9de90cbda41ff6eea009cc1a4f5b1813b8df`
- 7265 OM-1MarkII 10400x7792, 6.980 bpp, variable, bits/sample 16, tag 1, `c7bd43b29ed89542058534b867fa894b8550d1960503cf4b4cb9f5912fd242b3`
- 7266 OM-1MarkII 5220x3912, 8.145 bpp, variable, bits/sample 16, tag 1, `1c994e4bf5aa4e48d6ec97a1f83558184a866f71bca2b5b1bf914a159927e199`
- 7267 OM-1MarkII 10386x7792, 8.450 bpp, variable, bits/sample 16, tag 1, `5c4845bcf87d868c1b770d7e92e574e148d82acb2806cddd9df5a7a47d7cd756`
- 7268 OM-1MarkII 5220x3912, 8.136 bpp, variable, bits/sample 16, tag 1, `a5ee1e874d7aa357192173e12695627f90a8800a272b6c6e4959f029afb59837`
- 7269 OM-1MarkII 8172x6132, 8.794 bpp, variable, bits/sample 16, tag 1, `dd2a6c1c4ca4d86201207925477e2ea8e50ebd53d7df9117847093f5023540ec`
- 7270 OM-1MarkII 5220x3912, 8.114 bpp, variable, bits/sample 16, tag 1, `e4f3583f0bfb1efb0f40b201c5bb0cb1c30ace875a7f96d93fa7dddcc6966f5f`
- 7796 OM-3 5220x3912, 7.764 bpp, variable, bits/sample 16, tag 1, `1cee7deb661e45101ab3ca6c4240d24ed949b167ed423703fca15c09dd8ec176`
- 7797 OM-3 8180x6132, 6.993 bpp, variable, bits/sample 16, tag 1, `318e35647d93b2c598c0fec1d0d075336d2e2f5e6930faee05f32182c9a8ac5f`
- 7798 OM-3 5220x3912, 7.944 bpp, variable, bits/sample 16, tag 1, `6fab41a21d5c8c0469619049888b0a36c7b260d893e3c35c174044b7293e9d43`
- 7799 OM-3 10400x7792, 6.760 bpp, variable, bits/sample 16, tag 1, `9da7407d27007320c5bcf4e4d0b8c5c7bb533669cf4fabdf4e6a4b567cf318cc`
- 7800 OM-3 5220x3912, 7.849 bpp, variable, bits/sample 16, tag 1, `5640fb1a2ceff83d3678f46a7acdabd9ec393d318718c9c48a9c650afe7a7c58`
- 7801 OM-3 10386x7792, 8.208 bpp, variable, bits/sample 16, tag 1, `8832599870d20a96f28897e3e28d9705a4bd05871c9833c7c60a8b59d7d64b82`
- 7802 OM-3 5220x3912, 7.851 bpp, variable, bits/sample 16, tag 1, `2f8c0363376fe1c4f669f1c6c881611e8a71e39320bbac3c691405583b671cf2`
- 7803 OM-3 8172x6132, 8.446 bpp, variable, bits/sample 16, tag 1, `63a5b4da41fdbe8b31213ca7a11408dfd0453d893f17ac09a73471580ffbd8f0`
- 7804 OM-3 5220x3912, 7.916 bpp, variable, bits/sample 16, tag 1, `bcc05bd57e78cbbb308a596f97987975f7167b17768d8c2d536c87e0c34298e0`
- 8549 OM-5MarkII 5240x3912, 6.913 bpp, variable, bits/sample 16, tag 1, `c6fe861982ddc18464cf6858d2700f6813cc3a17956bcb12d1179212c999c76a`
- 8550 OM-5MarkII 5240x3912, 6.926 bpp, variable, bits/sample 16, tag 1, `8ebb09fb177f29f88faab15a1b1498182448a4b6d65dc5a2f533d5d5b5de1be0`
- 8552 OM-5MarkII 8200x6132, 6.259 bpp, variable, bits/sample 16, tag 1, `4d79adadf1f736cdbd666bc5f750ee75235b365ecb5fa8dcbc6cd7ca461343ed`
- 8553 OM-5MarkII 10400x7792, 6.212 bpp, variable, bits/sample 16, tag 1, `6c34d583e2c98840828fa500e54e47f270f138dfc697a9a7cd084575305d3c9f`
- 8554 OM-5MarkII 5240x3912, 6.784 bpp, variable, bits/sample 16, tag 1, `de530604f60a7e4f867ff8bf7889fc8b49fbe3e93f660ba72d13dccabe5bc583`
- 8609 SP550UZ 3088x2309, 12.000 bpp, packed-12, bits/sample 12, tag 1, `05f49918e1b1894c3abd2b5451b356f7a00adb1c8568abc5babff33fcade1bb2`

The tool measures only the TIFF structure and decodes nothing.

## Reproduce
    python tools/pixls_samples.py download ../orf-samples
    python tools/pixls_samples.py check ../orf-samples/*
    python tools/orf_signature.py ../orf-samples/* > sig.csv
    python -c "import csv,collections;R=list(csv.DictReader(open('sig.csv')));print(collections.Counter((r['compression_tag'],r['bits_per_sample'],r['size_class']) for r in R));v=[float(r['bpp']) for r in R if r['size_class']=='variable'];print(len(v),min(v),max(v))"
