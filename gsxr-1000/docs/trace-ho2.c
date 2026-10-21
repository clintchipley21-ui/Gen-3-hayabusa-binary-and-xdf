
// ===== FUNCTION 0x40bb0 (FUN_00040bac) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00040bac(void)

{
  byte bVar1;
  ushort uVar2;
  ushort uVar3;
  int unaff_gp;
  uint uVar4;
  uint uVar5;
  
  uVar3 = _DAT_fef008be;
  uVar2 = DAT_00155ab2;
  bVar1 = *(byte *)(unaff_gp + -0x60f8);
  uVar5 = (uint)_DAT_fef008c2;
  uVar4 = FUN_000a1fca(0x154fdc,DAT_fef02674);
  _DAT_fef008c4 = (undefined2)uVar4;
  if ((((bVar1 & 1) == 1) && (uVar4 <= uVar5)) && (uVar3 < uVar2)) {
    *(byte *)(unaff_gp + -0x60f8) = *(byte *)(unaff_gp + -0x60f8) & 0xfd;
    *(byte *)(unaff_gp + -0x60f8) = *(byte *)(unaff_gp + -0x60f8) | 4;
  }
  return;
}


// ===== FUNCTION 0x3e402 (FUN_0003e3fa) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0003e3fa(void)

{
  undefined1 uVar1;
  int unaff_gp;
  
  uVar1 = *(undefined1 *)(unaff_gp + -0x5bc0);
  _DAT_fef00890 = FUN_000a1fca(&DAT_00154f24,uVar1);
  _DAT_fef00892 = FUN_000a1fca(&PTR_DAT_00154f50,uVar1);
  return;
}


// ===== FUNCTION 0x3f8ce (FUN_0003f8b2) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0003f8b2(char param_1)

{
  undefined1 uVar1;
  int unaff_gp;
  byte extraout_var;
  int iVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_00155a62;
  uVar1 = *(undefined1 *)(unaff_gp + -0x5bbd);
  FUN_000a1fca(0x154ff0,*(undefined2 *)(unaff_gp + -0x5c6c));
  DAT_fef00acc = extraout_var;
  iVar2 = FUN_000a1fca(0x155004,uVar1);
  DAT_fef00acd = (byte)((uint)iVar2 >> 8);
  _DAT_fef00abc =
       FUN_000a1cc2((int)((uint)DAT_fef00acc *
                         ((int)(((iVar2 >> 8) + 0x180) * (uVar3 - 0x8000)) / 4)) / 0x4000 + 0x8000,
                    0xffff,0);
  if (param_1 != '\0') {
    _DAT_fef00abe =
         FUN_000a1cc2((int)((uint)DAT_fef00acc *
                           ((int)((DAT_fef00acd + 0x180) * (DAT_00155a64 - 0x8000)) / 4)) / 0x4000 +
                      0x8000,0xffff,0);
  }
  return;
}


// ===== FUNCTION 0x3c3e0 (FUN_0003c3b0) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0003c3b0(int param_1)

{
  byte bVar1;
  char cVar2;
  ushort uVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  ushort uVar7;
  int unaff_gp;
  undefined4 uVar8;
  char cVar9;
  ushort uVar10;
  ushort uVar11;
  ushort uVar12;
  undefined1 unaff_r22;
  undefined2 unaff_r23;
  ushort *puVar13;
  undefined2 unaff_r24;
  uint uVar14;
  bool bVar15;
  int iVar16;
  int unaff_r29;
  int unaff_ep;
  byte bStack00000002;
  byte bStack00000003;
  undefined4 in_stack_00000004;
  char cStack00000009;
  char cStack0000000a;
  char cStack0000000b;
  ushort uStack0000000e;
  ushort uStack00000012;
  ushort uStack00000016;
  ushort uStack00000018;
  ushort uStack0000001a;
  ushort uStack0000001c;
  ushort uStack0000001e;
  ushort uStack00000020;
  ushort uStack00000022;
  ushort uStack00000024;
  ushort uStack00000026;
  ushort uStack00000028;
  ushort uStack0000002a;
  ushort uStack0000002c;
  ushort uStack0000002e;
  ushort in_stack_00000030;
  ushort uStack00000032;
  ushort uStack00000036;
  ushort uStack0000003a;
  
  *(undefined2 *)(unaff_ep + 0x30) = unaff_r24;
  *(undefined2 *)(unaff_ep + 0x2e) = unaff_r23;
  *(undefined1 *)(unaff_ep + 5) = unaff_r22;
  iVar16 = param_1 * 2;
  uStack0000003a = *(ushort *)(&DAT_00155884 + iVar16);
  uVar12 = *(ushort *)(unaff_gp + -0x5c86);
  uStack00000032 = _DAT_fef01e44;
  cVar9 = FUN_00049000();
  uVar3 = *(ushort *)(unaff_gp + -0x5c14);
  uStack00000036 = *(ushort *)(unaff_r29 + 0x28);
  uVar5 = *(ushort *)(&DAT_febf5ff0 + iVar16);
  uStack00000012 = *(ushort *)(unaff_gp + -0x5c10);
  uVar6 = *(ushort *)(&DAT_fef00e4e + iVar16);
  puVar13 = (ushort *)(iVar16 + unaff_r29);
  uVar4 = *puVar13;
  uVar7 = *(ushort *)(&DAT_febf6004 + iVar16);
  uVar10 = *(ushort *)(unaff_gp + -0x5c38);
  uStack0000000e = FUN_000a201e(&PTR_DAT_00154f94,*(undefined2 *)(unaff_gp + -0x5c6c),uVar12);
  uVar10 = FUN_000a1b5c(uVar10 - 0x8000);
  uVar14 = (uint)*(byte *)(param_1 + unaff_r29 + 0x36);
  cStack00000009 = FUN_0003c2b8(param_1);
  cStack0000000a = FUN_0003be3a(param_1);
  bVar1 = *(byte *)(unaff_gp + -0x57b6);
  bStack00000002 = (byte)(((uint)*(byte *)(unaff_r29 + 0x41) << 0x1c) >> 0x1f);
  bStack00000003 = (byte)(((uint)*(byte *)(unaff_gp + -0x60fd) << 0x1d) >> 0x1f);
  if (param_1 == 0) {
    uStack00000016 = *(ushort *)(unaff_gp + -0x5fe4);
  }
  else {
    uStack00000016 = *(ushort *)(unaff_gp + -0x5fe2);
  }
  uVar11 = FUN_000a1b5c((uint)uStack00000016 - (uint)puVar13[6]);
  cVar2 = *(char *)(unaff_gp + -0x5bbe);
  cStack0000000b = *(char *)(param_1 + unaff_r29 + 0x3c);
  if (param_1 == 0) {
    uVar8 = 0x27;
  }
  else {
    uVar8 = 0x2b;
  }
  FUN_0005c0a2(uVar8);
  if (((((cVar9 == '\x01') && (uStack00000018 <= uStack00000032)) && (uStack0000001a <= uVar12)) &&
      (((uVar12 <= uStack0000001c && (uStack0000001e <= uVar3)) &&
       ((uVar3 < uStack0000000e && ((uStack00000020 <= uVar5 && (uVar5 < uStack00000022)))))))) &&
     (((uVar6 < uStack00000024 &&
       ((((((uStack00000026 <= uStack00000012 && (uStack00000012 < uStack00000028)) &&
           (uStack00000036 < uStack0000002a)) &&
          ((uVar10 < uStack0000002c && (in_stack_00000004._1_1_ == -0x80)))) &&
         ((in_stack_00000030 <= uVar7 && ((uVar7 < 0x8001 && (bStack00000002 == 0)))))) &&
        (bStack00000003 == 0)))) &&
      ((((bVar1 & 1) == 0 && (uVar11 <= uStack0000003a)) && (cVar2 == cStack0000000b)))))) {
    if (cStack00000009 == '\x01') {
      uVar14 = FUN_000a1cd2(uVar14,1);
    }
    bVar15 = uStack0000002e <= uVar4 || in_stack_00000004._2_1_ <= uVar14;
    uVar12 = FUN_000a1cf6(uVar4,1);
    if (((uStack0000002e <= uVar4 || in_stack_00000004._2_1_ <= uVar14) && (cStack0000000a == '\0'))
       && (uVar14 < in_stack_00000004._2_1_)) {
      FUN_0003c2de(param_1,1);
    }
  }
  else {
    bVar15 = false;
    uVar12 = 0;
    uVar14 = 0;
  }
  FUN_0003be5a(param_1,bVar15);
  *puVar13 = uVar12;
  *(char *)(param_1 + unaff_r29 + 0x36) = (char)uVar14;
  *(ushort *)(unaff_r29 + 0x2c) = uStack0000000e;
  puVar13[6] = uStack00000016;
  *(char *)(param_1 + unaff_r29 + 0x3c) = cVar2;
  return;
}


// ===== FUNCTION 0x3f8e0 (FUN_0003f8b2) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0003f8b2(char param_1)

{
  undefined1 uVar1;
  int unaff_gp;
  byte extraout_var;
  int iVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_00155a62;
  uVar1 = *(undefined1 *)(unaff_gp + -0x5bbd);
  FUN_000a1fca(0x154ff0,*(undefined2 *)(unaff_gp + -0x5c6c));
  DAT_fef00acc = extraout_var;
  iVar2 = FUN_000a1fca(0x155004,uVar1);
  DAT_fef00acd = (byte)((uint)iVar2 >> 8);
  _DAT_fef00abc =
       FUN_000a1cc2((int)((uint)DAT_fef00acc *
                         ((int)(((iVar2 >> 8) + 0x180) * (uVar3 - 0x8000)) / 4)) / 0x4000 + 0x8000,
                    0xffff,0);
  if (param_1 != '\0') {
    _DAT_fef00abe =
         FUN_000a1cc2((int)((uint)DAT_fef00acc *
                           ((int)((DAT_fef00acd + 0x180) * (DAT_00155a64 - 0x8000)) / 4)) / 0x4000 +
                      0x8000,0xffff,0);
  }
  return;
}


// ===== FUNCTION 0x4b93e (FUN_0004b920) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0004b920(void)

{
  undefined1 uVar1;
  int unaff_gp;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar1 = *(undefined1 *)(unaff_gp + -0x5bc0);
  iVar2 = FUN_00083184();
  uVar5 = (uint)DAT_fef00d26;
  uVar4 = (uint)_DAT_fef00ce6;
  uVar3 = FUN_000a1fca(&PTR_DAT_00156654,uVar1);
  _DAT_fef00ce4 = (undefined2)uVar3;
  if (iVar2 == 0) {
    iVar2 = (uint)(uVar3 <= uVar4) + -((int)(uVar5 << 0x1d) >> 0x1f) * (uint)(uVar3 > uVar4);
    _DAT_fef00ce6 = FUN_000a1cf6(uVar4,1);
  }
  else {
    iVar2 = 0;
    _DAT_fef00ce6 = 0;
  }
  if (iVar2 == 1) {
    DAT_fef00d26 = DAT_fef00d26 | 4;
  }
  else {
    DAT_fef00d26 = DAT_fef00d26 & 0xfb;
  }
  return;
}


// ===== FUNCTION 0x496ba (FUN_0004968c) =====

void FUN_0004968c(void)

{
  undefined2 uVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  char cVar6;
  int unaff_gp;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  
  cVar6 = DAT_001670f8;
  uVar1 = *(undefined2 *)(unaff_gp + -0x5c86);
  uVar2 = *(undefined2 *)(unaff_gp + -0x5a1a);
  uVar3 = *(undefined2 *)(unaff_gp + -0x5a18);
  uVar4 = *(undefined2 *)(unaff_gp + -0x5a16);
  uVar5 = *(undefined2 *)(unaff_gp + -0x5a14);
  iVar7 = FUN_000a201e(&DAT_00156e88,uVar2,uVar1);
  iVar7 = iVar7 >> 8;
  iVar8 = FUN_000a201e(&DAT_00156ea4,uVar3,uVar1);
  iVar8 = iVar8 >> 8;
  iVar9 = FUN_000a201e(&DAT_00156ec0,uVar4,uVar1);
  iVar9 = iVar9 >> 8;
  iVar10 = FUN_000a201e(&DAT_00156edc,uVar5,uVar1);
  iVar10 = iVar10 >> 8;
  iVar11 = FUN_000a201e(&DAT_00156ef8,uVar2,uVar1);
  iVar11 = iVar11 >> 8;
  iVar12 = FUN_000a201e(&DAT_00156f14,uVar3,uVar1);
  iVar12 = iVar12 >> 8;
  iVar13 = FUN_000a201e(&DAT_00156f30,uVar4,uVar1);
  iVar14 = FUN_000a201e(&DAT_00156f4c,uVar5,uVar1);
  iVar14 = iVar14 >> 8;
  if (cVar6 == '\0') {
    DAT_fef00d20 = FUN_000a1cac(iVar10 + iVar9 + iVar8 + iVar7 + -0x180,0xff,0);
    DAT_fef00d21 = 0x80;
    DAT_fef00d22 = FUN_000a1cac(iVar14 + (iVar13 >> 8) + iVar12 + iVar11 + -0x180,0xff,0);
    DAT_fef00d23 = 0x80;
  }
  else {
    if (cVar6 == '\x01') {
      DAT_fef00d20 = FUN_000a1cac(iVar10 + iVar7 + -0x80,0xff,0);
      DAT_fef00d21 = FUN_000a1cac(iVar9 + iVar8 + -0x80,0xff,0);
      DAT_fef00d22 = FUN_000a1cac(iVar14 + iVar11 + -0x80,0xff,0);
      iVar14 = iVar12;
    }
    else {
      if (cVar6 != '\x02') {
        return;
      }
      DAT_fef00d20 = FUN_000a1cac(iVar8 + iVar7 + -0x80,0xff,0);
      DAT_fef00d21 = FUN_000a1cac(iVar10 + iVar9 + -0x80,0xff,0);
      DAT_fef00d22 = FUN_000a1cac(iVar12 + iVar11 + -0x80,0xff,0);
    }
    DAT_fef00d23 = FUN_000a1cac((iVar13 >> 8) + iVar14 + -0x80,0xff,0);
  }
  return;
}


// ===== FUNCTION 0x498ac (FUN_000498ac) =====

void FUN_000498ac(uint param_1)

{
  byte bVar1;
  undefined **ppuVar2;
  int unaff_gp;
  int iVar3;
  
  param_1 = param_1 & 0xff;
  bVar1 = *(byte *)(param_1 + 0xfef00ce8);
  if (bVar1 != 0) {
    if (bVar1 == 1) {
      ppuVar2 = &PTR_PTR_DAT_00155d4c;
    }
    else if (bVar1 < 3) {
      ppuVar2 = &PTR_PTR_DAT_00155d54;
    }
    else {
      if (3 < bVar1) goto LAB_00049902;
      ppuVar2 = &PTR_PTR_DAT_00155d5c;
    }
    iVar3 = FUN_000a2344(ppuVar2[param_1],*(undefined2 *)(unaff_gp + -0x5c20),
                         *(undefined2 *)(unaff_gp + -0x5c86));
    iVar3 = iVar3 >> 8;
    if (((iVar3 == 0) || (iVar3 == 1)) || (iVar3 == 2)) goto LAB_00049904;
  }
LAB_00049902:
  iVar3 = 2;
LAB_00049904:
  *(char *)(param_1 + 0xfef00cec) = (char)iVar3;
  return;
}


// ===== FUNCTION 0x49a4e (FUN_00049a4e) =====

void FUN_00049a4e(uint param_1)

{
  byte bVar1;
  undefined **ppuVar2;
  int unaff_gp;
  int iVar3;
  
  param_1 = param_1 & 0xff;
  bVar1 = *(byte *)(param_1 + 0xfef00d10);
  if (bVar1 == 0) {
LAB_00049a7a:
    iVar3 = 0;
  }
  else {
    if (bVar1 == 1) {
      ppuVar2 = &PTR_PTR_DAT_00155d6c;
    }
    else if (bVar1 < 3) {
      ppuVar2 = &PTR_PTR_DAT_00155d74;
    }
    else {
      if (3 < bVar1) goto LAB_00049a7a;
      ppuVar2 = &PTR_PTR_DAT_00155d7c;
    }
    iVar3 = FUN_000a2344(ppuVar2[param_1],*(undefined2 *)(unaff_gp + -0x5c20),
                         *(undefined2 *)(unaff_gp + -0x5c86));
    iVar3 = iVar3 >> 8;
    if ((iVar3 != 0) && (iVar3 != 1)) {
      iVar3 = 2;
    }
  }
  *(char *)(param_1 + 0xfef00d14) = (char)iVar3;
  return;
}


// ===== FUNCTION 0x49b6e (FUN_00049b6e) =====

void FUN_00049b6e(uint param_1)

{
  int unaff_gp;
  int iVar1;
  
  iVar1 = FUN_000a2344((&PTR_PTR_DAT_00155d64)[param_1 & 0xff],*(undefined2 *)(unaff_gp + -0x5c14),
                       *(undefined2 *)(unaff_gp + -0x5c86));
  iVar1 = iVar1 >> 8;
  if ((iVar1 != 0) && (iVar1 != 1)) {
    iVar1 = 2;
  }
  *(char *)((param_1 & 0xff) + 0xfef00cee) = (char)iVar1;
  return;
}


// ===== FUNCTION 0x49c4c (FUN_00049c4c) =====

void FUN_00049c4c(uint param_1)

{
  int unaff_gp;
  int iVar1;
  
  iVar1 = FUN_000a2344(*(undefined4 *)(&LAB_00155d84 + (param_1 & 0xff) * 4),
                       *(undefined2 *)(unaff_gp + -0x5c14),*(undefined2 *)(unaff_gp + -0x5c86));
  iVar1 = iVar1 >> 8;
  if ((iVar1 != 0) && (iVar1 != 1)) {
    iVar1 = 2;
  }
  *(char *)((param_1 & 0xff) + 0xfef00d16) = (char)iVar1;
  return;
}

