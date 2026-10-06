
// ===== FUNCTION 0x28d20 (FUN_00028ca6) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00028ca6(void)

{
  byte bVar1;
  char cVar2;
  byte bVar3;
  undefined2 uVar4;
  int unaff_gp;
  undefined *puVar5;
  undefined2 uVar6;
  undefined1 extraout_var;
  undefined2 uVar7;
  int iVar8;
  undefined1 uVar9;
  
  uVar4 = _DAT_fef0262c;
  uVar6 = _DAT_fef005c0;
  uVar9 = DAT_febf5e8e;
  bVar3 = DAT_00154e16;
  bVar1 = *(byte *)(unaff_gp + -0x5ba6);
  cVar2 = *(char *)(unaff_gp + -0x5bbe);
  uVar7 = *(undefined2 *)(unaff_gp + -0x5c86);
  iVar8 = FUN_00028e86();
  if (iVar8 == 1) {
    if (bVar1 != 0) {
      if (bVar1 == 1) {
        uVar6 = FUN_000a201e(&DAT_0015122c,uVar4,cVar2);
        puVar5 = &DAT_00151280;
      }
      else if (bVar1 < 3) {
        uVar6 = FUN_000a201e(&DAT_00151248,uVar4,cVar2);
        puVar5 = &DAT_0015129c;
      }
      else {
        if (3 < bVar1) {
          DAT_febf5e8e = uVar9;
          DAT_fef00526 = 0;
          _DAT_fef005c0 = uVar6;
          return;
        }
        uVar6 = FUN_000a201e(&DAT_00151264,uVar4,cVar2);
        puVar5 = &DAT_001512b8;
      }
      FUN_000a201e(puVar5,uVar4,cVar2);
      uVar9 = extraout_var;
    }
  }
  else {
    if ((cVar2 == '\x01') || (iVar8 = FUN_0002963c(), iVar8 == 1)) {
      if (DAT_fef00526 < bVar3) {
        uVar7 = FUN_000a201e(&DAT_00151210,uVar7,bVar1);
      }
      else {
        uVar9 = 0x40;
        uVar7 = 0;
      }
      DAT_fef00526 = FUN_000a1cd2(DAT_fef00526,1);
      DAT_febf5e8e = uVar9;
      _DAT_fef005c0 = uVar7;
      return;
    }
    uVar6 = FUN_000a201e(&DAT_00151210,uVar7,bVar1);
  }
  DAT_fef00526 = 0;
  _DAT_fef005c0 = uVar6;
  DAT_febf5e8e = uVar9;
  return;
}


// ===== FUNCTION 0x28d38 (FUN_00028ca6) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00028ca6(void)

{
  byte bVar1;
  char cVar2;
  byte bVar3;
  undefined2 uVar4;
  int unaff_gp;
  undefined *puVar5;
  undefined2 uVar6;
  undefined1 extraout_var;
  undefined2 uVar7;
  int iVar8;
  undefined1 uVar9;
  
  uVar4 = _DAT_fef0262c;
  uVar6 = _DAT_fef005c0;
  uVar9 = DAT_febf5e8e;
  bVar3 = DAT_00154e16;
  bVar1 = *(byte *)(unaff_gp + -0x5ba6);
  cVar2 = *(char *)(unaff_gp + -0x5bbe);
  uVar7 = *(undefined2 *)(unaff_gp + -0x5c86);
  iVar8 = FUN_00028e86();
  if (iVar8 == 1) {
    if (bVar1 != 0) {
      if (bVar1 == 1) {
        uVar6 = FUN_000a201e(&DAT_0015122c,uVar4,cVar2);
        puVar5 = &DAT_00151280;
      }
      else if (bVar1 < 3) {
        uVar6 = FUN_000a201e(&DAT_00151248,uVar4,cVar2);
        puVar5 = &DAT_0015129c;
      }
      else {
        if (3 < bVar1) {
          DAT_febf5e8e = uVar9;
          DAT_fef00526 = 0;
          _DAT_fef005c0 = uVar6;
          return;
        }
        uVar6 = FUN_000a201e(&DAT_00151264,uVar4,cVar2);
        puVar5 = &DAT_001512b8;
      }
      FUN_000a201e(puVar5,uVar4,cVar2);
      uVar9 = extraout_var;
    }
  }
  else {
    if ((cVar2 == '\x01') || (iVar8 = FUN_0002963c(), iVar8 == 1)) {
      if (DAT_fef00526 < bVar3) {
        uVar7 = FUN_000a201e(&DAT_00151210,uVar7,bVar1);
      }
      else {
        uVar9 = 0x40;
        uVar7 = 0;
      }
      DAT_fef00526 = FUN_000a1cd2(DAT_fef00526,1);
      DAT_febf5e8e = uVar9;
      _DAT_fef005c0 = uVar7;
      return;
    }
    uVar6 = FUN_000a201e(&DAT_00151210,uVar7,bVar1);
  }
  DAT_fef00526 = 0;
  _DAT_fef005c0 = uVar6;
  DAT_febf5e8e = uVar9;
  return;
}


// ===== FUNCTION 0x53994 (FUN_000538fa) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000538fa(void)

{
  undefined2 uVar1;
  ushort uVar2;
  int unaff_gp;
  undefined **ppuVar3;
  ushort uVar4;
  ushort uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  ushort uVar10;
  uint uVar11;
  ushort uVar12;
  uint uVar13;
  ushort uVar14;
  uint uVar15;
  uint uVar16;
  ushort uVar17;
  uint uVar18;
  uint uVar19;
  uint uVar20;
  undefined2 uStack_3a;
  undefined2 uStack_30;
  
  uVar5 = _DAT_febf602e;
  uVar4 = _DAT_febf602c;
  uVar2 = DAT_00167016;
  uVar1 = *(undefined2 *)(unaff_gp + -0x5c86);
  uStack_3a = *(undefined2 *)(unaff_gp + -0x5f34);
  uStack_30 = *(undefined2 *)(unaff_gp + -0x5f32);
  uVar20 = (uint)_DAT_febf602c;
  uVar19 = (uint)_DAT_febf602e;
  uVar17 = *(ushort *)(unaff_gp + -0x5f30);
  uVar18 = (uint)uVar17;
  uVar14 = *(ushort *)(unaff_gp + -0x5f2a);
  uVar15 = (uint)uVar14;
  uVar12 = *(ushort *)(unaff_gp + -0x5f2e);
  uVar13 = (uint)uVar12;
  uVar10 = *(ushort *)(unaff_gp + -0x5f28);
  uVar11 = (uint)uVar10;
  uVar6 = FUN_000a201e(&PTR_DAT_00157c90,*(undefined2 *)(unaff_gp + -0x5c3c),uVar1);
  uVar7 = FUN_000a1ba0(0x8000 - uVar6,0);
  uVar16 = uVar7 & 0xffff;
  iVar8 = FUN_000a1fca(&PTR_DAT_00157850,uVar1);
  if ((uint)DAT_fef00f2f < (uint)(iVar8 >> 8)) goto LAB_00053a48;
  if (uVar6 < uVar20) {
    uVar18 = uVar20 - uVar6 & 0xffff;
    if ((*(byte *)(unaff_gp + -0x5f21) & 4) == 0) {
      uVar9 = FUN_000a1fca(&PTR_DAT_00157ad4,uVar1);
      uStack_30 = (undefined2)uVar9;
      if (uVar9 < uVar18) {
        ppuVar3 = &PTR_DAT_00157a1c;
      }
      else {
        ppuVar3 = &PTR_DAT_00157a78;
      }
    }
    else {
      uVar9 = FUN_000a1fca(&PTR_DAT_001579c0,uVar1);
      uStack_3a = (undefined2)uVar9;
      if (uVar9 < uVar18) {
        ppuVar3 = &PTR_DAT_00157908;
      }
      else {
        ppuVar3 = &PTR_DAT_00157964;
      }
    }
    uVar18 = FUN_000a1fca(ppuVar3,uVar1);
    uVar4 = FUN_000a1ba0(uVar20 - uVar18,uVar6);
LAB_00053a0e:
    uVar17 = (ushort)uVar18;
    uVar12 = (ushort)uVar13;
  }
  else if (uVar20 < uVar6) {
    if (*(ushort *)(unaff_gp + -0x5f26) < uVar2) {
      ppuVar3 = &PTR_DAT_00157b8c;
    }
    else {
      ppuVar3 = &PTR_DAT_00157b30;
    }
    uVar13 = FUN_000a1fca(ppuVar3,uVar1);
    uVar4 = FUN_000a1c02(uVar13 + uVar20,uVar6);
    goto LAB_00053a0e;
  }
  if (uVar16 < uVar19) {
    uVar15 = FUN_000a1fca(&PTR_DAT_00157be8,uVar1);
    uVar5 = FUN_000a1ba0(uVar19 - uVar15,uVar16);
  }
  else {
    if (uVar16 <= uVar19) goto LAB_00053a48;
    uVar11 = FUN_000a1fca(&PTR_DAT_00157c44,uVar1);
    uVar5 = FUN_000a1c02(uVar11 + uVar19,uVar16);
  }
  uVar14 = (ushort)uVar15;
  uVar10 = (ushort)uVar11;
LAB_00053a48:
  *(char *)(unaff_gp + -0x5f22) = (char)((uint)iVar8 >> 8);
  *(ushort *)(unaff_gp + -0x5f28) = uVar10;
  *(ushort *)(unaff_gp + -0x5f2e) = uVar12;
  *(ushort *)(unaff_gp + -0x5f2a) = uVar14;
  *(ushort *)(unaff_gp + -0x5f30) = uVar17;
  *(short *)(unaff_gp + -0x5f2c) = (short)uVar7;
  *(undefined2 *)(unaff_gp + -0x5f34) = uStack_3a;
  *(short *)(unaff_gp + -0x5f36) = (short)uVar6;
  _DAT_febf602c = uVar4;
  _DAT_febf602e = uVar5;
  *(undefined2 *)(unaff_gp + -0x5f32) = uStack_30;
  return;
}


// ===== FUNCTION 0x539d4 (FUN_000538fa) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000538fa(void)

{
  undefined2 uVar1;
  ushort uVar2;
  int unaff_gp;
  undefined **ppuVar3;
  ushort uVar4;
  ushort uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  ushort uVar10;
  uint uVar11;
  ushort uVar12;
  uint uVar13;
  ushort uVar14;
  uint uVar15;
  uint uVar16;
  ushort uVar17;
  uint uVar18;
  uint uVar19;
  uint uVar20;
  undefined2 uStack_3a;
  undefined2 uStack_30;
  
  uVar5 = _DAT_febf602e;
  uVar4 = _DAT_febf602c;
  uVar2 = DAT_00167016;
  uVar1 = *(undefined2 *)(unaff_gp + -0x5c86);
  uStack_3a = *(undefined2 *)(unaff_gp + -0x5f34);
  uStack_30 = *(undefined2 *)(unaff_gp + -0x5f32);
  uVar20 = (uint)_DAT_febf602c;
  uVar19 = (uint)_DAT_febf602e;
  uVar17 = *(ushort *)(unaff_gp + -0x5f30);
  uVar18 = (uint)uVar17;
  uVar14 = *(ushort *)(unaff_gp + -0x5f2a);
  uVar15 = (uint)uVar14;
  uVar12 = *(ushort *)(unaff_gp + -0x5f2e);
  uVar13 = (uint)uVar12;
  uVar10 = *(ushort *)(unaff_gp + -0x5f28);
  uVar11 = (uint)uVar10;
  uVar6 = FUN_000a201e(&PTR_DAT_00157c90,*(undefined2 *)(unaff_gp + -0x5c3c),uVar1);
  uVar7 = FUN_000a1ba0(0x8000 - uVar6,0);
  uVar16 = uVar7 & 0xffff;
  iVar8 = FUN_000a1fca(&PTR_DAT_00157850,uVar1);
  if ((uint)DAT_fef00f2f < (uint)(iVar8 >> 8)) goto LAB_00053a48;
  if (uVar6 < uVar20) {
    uVar18 = uVar20 - uVar6 & 0xffff;
    if ((*(byte *)(unaff_gp + -0x5f21) & 4) == 0) {
      uVar9 = FUN_000a1fca(&PTR_DAT_00157ad4,uVar1);
      uStack_30 = (undefined2)uVar9;
      if (uVar9 < uVar18) {
        ppuVar3 = &PTR_DAT_00157a1c;
      }
      else {
        ppuVar3 = &PTR_DAT_00157a78;
      }
    }
    else {
      uVar9 = FUN_000a1fca(&PTR_DAT_001579c0,uVar1);
      uStack_3a = (undefined2)uVar9;
      if (uVar9 < uVar18) {
        ppuVar3 = &PTR_DAT_00157908;
      }
      else {
        ppuVar3 = &PTR_DAT_00157964;
      }
    }
    uVar18 = FUN_000a1fca(ppuVar3,uVar1);
    uVar4 = FUN_000a1ba0(uVar20 - uVar18,uVar6);
LAB_00053a0e:
    uVar17 = (ushort)uVar18;
    uVar12 = (ushort)uVar13;
  }
  else if (uVar20 < uVar6) {
    if (*(ushort *)(unaff_gp + -0x5f26) < uVar2) {
      ppuVar3 = &PTR_DAT_00157b8c;
    }
    else {
      ppuVar3 = &PTR_DAT_00157b30;
    }
    uVar13 = FUN_000a1fca(ppuVar3,uVar1);
    uVar4 = FUN_000a1c02(uVar13 + uVar20,uVar6);
    goto LAB_00053a0e;
  }
  if (uVar16 < uVar19) {
    uVar15 = FUN_000a1fca(&PTR_DAT_00157be8,uVar1);
    uVar5 = FUN_000a1ba0(uVar19 - uVar15,uVar16);
  }
  else {
    if (uVar16 <= uVar19) goto LAB_00053a48;
    uVar11 = FUN_000a1fca(&PTR_DAT_00157c44,uVar1);
    uVar5 = FUN_000a1c02(uVar11 + uVar19,uVar16);
  }
  uVar14 = (ushort)uVar15;
  uVar10 = (ushort)uVar11;
LAB_00053a48:
  *(char *)(unaff_gp + -0x5f22) = (char)((uint)iVar8 >> 8);
  *(ushort *)(unaff_gp + -0x5f28) = uVar10;
  *(ushort *)(unaff_gp + -0x5f2e) = uVar12;
  *(ushort *)(unaff_gp + -0x5f2a) = uVar14;
  *(ushort *)(unaff_gp + -0x5f30) = uVar17;
  *(short *)(unaff_gp + -0x5f2c) = (short)uVar7;
  *(undefined2 *)(unaff_gp + -0x5f34) = uStack_3a;
  *(short *)(unaff_gp + -0x5f36) = (short)uVar6;
  _DAT_febf602c = uVar4;
  _DAT_febf602e = uVar5;
  *(undefined2 *)(unaff_gp + -0x5f32) = uStack_30;
  return;
}


// ===== FUNCTION 0x539f0 (FUN_000538fa) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000538fa(void)

{
  undefined2 uVar1;
  ushort uVar2;
  int unaff_gp;
  undefined **ppuVar3;
  ushort uVar4;
  ushort uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  ushort uVar10;
  uint uVar11;
  ushort uVar12;
  uint uVar13;
  ushort uVar14;
  uint uVar15;
  uint uVar16;
  ushort uVar17;
  uint uVar18;
  uint uVar19;
  uint uVar20;
  undefined2 uStack_3a;
  undefined2 uStack_30;
  
  uVar5 = _DAT_febf602e;
  uVar4 = _DAT_febf602c;
  uVar2 = DAT_00167016;
  uVar1 = *(undefined2 *)(unaff_gp + -0x5c86);
  uStack_3a = *(undefined2 *)(unaff_gp + -0x5f34);
  uStack_30 = *(undefined2 *)(unaff_gp + -0x5f32);
  uVar20 = (uint)_DAT_febf602c;
  uVar19 = (uint)_DAT_febf602e;
  uVar17 = *(ushort *)(unaff_gp + -0x5f30);
  uVar18 = (uint)uVar17;
  uVar14 = *(ushort *)(unaff_gp + -0x5f2a);
  uVar15 = (uint)uVar14;
  uVar12 = *(ushort *)(unaff_gp + -0x5f2e);
  uVar13 = (uint)uVar12;
  uVar10 = *(ushort *)(unaff_gp + -0x5f28);
  uVar11 = (uint)uVar10;
  uVar6 = FUN_000a201e(&PTR_DAT_00157c90,*(undefined2 *)(unaff_gp + -0x5c3c),uVar1);
  uVar7 = FUN_000a1ba0(0x8000 - uVar6,0);
  uVar16 = uVar7 & 0xffff;
  iVar8 = FUN_000a1fca(&PTR_DAT_00157850,uVar1);
  if ((uint)DAT_fef00f2f < (uint)(iVar8 >> 8)) goto LAB_00053a48;
  if (uVar6 < uVar20) {
    uVar18 = uVar20 - uVar6 & 0xffff;
    if ((*(byte *)(unaff_gp + -0x5f21) & 4) == 0) {
      uVar9 = FUN_000a1fca(&PTR_DAT_00157ad4,uVar1);
      uStack_30 = (undefined2)uVar9;
      if (uVar9 < uVar18) {
        ppuVar3 = &PTR_DAT_00157a1c;
      }
      else {
        ppuVar3 = &PTR_DAT_00157a78;
      }
    }
    else {
      uVar9 = FUN_000a1fca(&PTR_DAT_001579c0,uVar1);
      uStack_3a = (undefined2)uVar9;
      if (uVar9 < uVar18) {
        ppuVar3 = &PTR_DAT_00157908;
      }
      else {
        ppuVar3 = &PTR_DAT_00157964;
      }
    }
    uVar18 = FUN_000a1fca(ppuVar3,uVar1);
    uVar4 = FUN_000a1ba0(uVar20 - uVar18,uVar6);
LAB_00053a0e:
    uVar17 = (ushort)uVar18;
    uVar12 = (ushort)uVar13;
  }
  else if (uVar20 < uVar6) {
    if (*(ushort *)(unaff_gp + -0x5f26) < uVar2) {
      ppuVar3 = &PTR_DAT_00157b8c;
    }
    else {
      ppuVar3 = &PTR_DAT_00157b30;
    }
    uVar13 = FUN_000a1fca(ppuVar3,uVar1);
    uVar4 = FUN_000a1c02(uVar13 + uVar20,uVar6);
    goto LAB_00053a0e;
  }
  if (uVar16 < uVar19) {
    uVar15 = FUN_000a1fca(&PTR_DAT_00157be8,uVar1);
    uVar5 = FUN_000a1ba0(uVar19 - uVar15,uVar16);
  }
  else {
    if (uVar16 <= uVar19) goto LAB_00053a48;
    uVar11 = FUN_000a1fca(&PTR_DAT_00157c44,uVar1);
    uVar5 = FUN_000a1c02(uVar11 + uVar19,uVar16);
  }
  uVar14 = (ushort)uVar15;
  uVar10 = (ushort)uVar11;
LAB_00053a48:
  *(char *)(unaff_gp + -0x5f22) = (char)((uint)iVar8 >> 8);
  *(ushort *)(unaff_gp + -0x5f28) = uVar10;
  *(ushort *)(unaff_gp + -0x5f2e) = uVar12;
  *(ushort *)(unaff_gp + -0x5f2a) = uVar14;
  *(ushort *)(unaff_gp + -0x5f30) = uVar17;
  *(short *)(unaff_gp + -0x5f2c) = (short)uVar7;
  *(undefined2 *)(unaff_gp + -0x5f34) = uStack_3a;
  *(short *)(unaff_gp + -0x5f36) = (short)uVar6;
  _DAT_febf602c = uVar4;
  _DAT_febf602e = uVar5;
  *(undefined2 *)(unaff_gp + -0x5f32) = uStack_30;
  return;
}


// ===== FUNCTION 0x539f8 (FUN_000538fa) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000538fa(void)

{
  undefined2 uVar1;
  ushort uVar2;
  int unaff_gp;
  undefined **ppuVar3;
  ushort uVar4;
  ushort uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  ushort uVar10;
  uint uVar11;
  ushort uVar12;
  uint uVar13;
  ushort uVar14;
  uint uVar15;
  uint uVar16;
  ushort uVar17;
  uint uVar18;
  uint uVar19;
  uint uVar20;
  undefined2 uStack_3a;
  undefined2 uStack_30;
  
  uVar5 = _DAT_febf602e;
  uVar4 = _DAT_febf602c;
  uVar2 = DAT_00167016;
  uVar1 = *(undefined2 *)(unaff_gp + -0x5c86);
  uStack_3a = *(undefined2 *)(unaff_gp + -0x5f34);
  uStack_30 = *(undefined2 *)(unaff_gp + -0x5f32);
  uVar20 = (uint)_DAT_febf602c;
  uVar19 = (uint)_DAT_febf602e;
  uVar17 = *(ushort *)(unaff_gp + -0x5f30);
  uVar18 = (uint)uVar17;
  uVar14 = *(ushort *)(unaff_gp + -0x5f2a);
  uVar15 = (uint)uVar14;
  uVar12 = *(ushort *)(unaff_gp + -0x5f2e);
  uVar13 = (uint)uVar12;
  uVar10 = *(ushort *)(unaff_gp + -0x5f28);
  uVar11 = (uint)uVar10;
  uVar6 = FUN_000a201e(&PTR_DAT_00157c90,*(undefined2 *)(unaff_gp + -0x5c3c),uVar1);
  uVar7 = FUN_000a1ba0(0x8000 - uVar6,0);
  uVar16 = uVar7 & 0xffff;
  iVar8 = FUN_000a1fca(&PTR_DAT_00157850,uVar1);
  if ((uint)DAT_fef00f2f < (uint)(iVar8 >> 8)) goto LAB_00053a48;
  if (uVar6 < uVar20) {
    uVar18 = uVar20 - uVar6 & 0xffff;
    if ((*(byte *)(unaff_gp + -0x5f21) & 4) == 0) {
      uVar9 = FUN_000a1fca(&PTR_DAT_00157ad4,uVar1);
      uStack_30 = (undefined2)uVar9;
      if (uVar9 < uVar18) {
        ppuVar3 = &PTR_DAT_00157a1c;
      }
      else {
        ppuVar3 = &PTR_DAT_00157a78;
      }
    }
    else {
      uVar9 = FUN_000a1fca(&PTR_DAT_001579c0,uVar1);
      uStack_3a = (undefined2)uVar9;
      if (uVar9 < uVar18) {
        ppuVar3 = &PTR_DAT_00157908;
      }
      else {
        ppuVar3 = &PTR_DAT_00157964;
      }
    }
    uVar18 = FUN_000a1fca(ppuVar3,uVar1);
    uVar4 = FUN_000a1ba0(uVar20 - uVar18,uVar6);
LAB_00053a0e:
    uVar17 = (ushort)uVar18;
    uVar12 = (ushort)uVar13;
  }
  else if (uVar20 < uVar6) {
    if (*(ushort *)(unaff_gp + -0x5f26) < uVar2) {
      ppuVar3 = &PTR_DAT_00157b8c;
    }
    else {
      ppuVar3 = &PTR_DAT_00157b30;
    }
    uVar13 = FUN_000a1fca(ppuVar3,uVar1);
    uVar4 = FUN_000a1c02(uVar13 + uVar20,uVar6);
    goto LAB_00053a0e;
  }
  if (uVar16 < uVar19) {
    uVar15 = FUN_000a1fca(&PTR_DAT_00157be8,uVar1);
    uVar5 = FUN_000a1ba0(uVar19 - uVar15,uVar16);
  }
  else {
    if (uVar16 <= uVar19) goto LAB_00053a48;
    uVar11 = FUN_000a1fca(&PTR_DAT_00157c44,uVar1);
    uVar5 = FUN_000a1c02(uVar11 + uVar19,uVar16);
  }
  uVar14 = (ushort)uVar15;
  uVar10 = (ushort)uVar11;
LAB_00053a48:
  *(char *)(unaff_gp + -0x5f22) = (char)((uint)iVar8 >> 8);
  *(ushort *)(unaff_gp + -0x5f28) = uVar10;
  *(ushort *)(unaff_gp + -0x5f2e) = uVar12;
  *(ushort *)(unaff_gp + -0x5f2a) = uVar14;
  *(ushort *)(unaff_gp + -0x5f30) = uVar17;
  *(short *)(unaff_gp + -0x5f2c) = (short)uVar7;
  *(undefined2 *)(unaff_gp + -0x5f34) = uStack_3a;
  *(short *)(unaff_gp + -0x5f36) = (short)uVar6;
  _DAT_febf602c = uVar4;
  _DAT_febf602e = uVar5;
  *(undefined2 *)(unaff_gp + -0x5f32) = uStack_30;
  return;
}


// ===== FUNCTION 0x56250 (FUN_000561d6) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000561d6(void)

{
  char cVar1;
  int unaff_gp;
  undefined1 extraout_var;
  uint uVar2;
  
  cVar1 = *(char *)(unaff_gp + -0x5bbe);
  if (cVar1 == '\x02') {
    uVar2 = (uint)DAT_001702b9;
  }
  else if (cVar1 == '\x04') {
    uVar2 = (uint)DAT_001702ba;
  }
  else if (cVar1 == '\b') {
    uVar2 = (uint)DAT_001702bb;
  }
  else if (cVar1 == '\x10') {
    uVar2 = (uint)DAT_001702bc;
  }
  else if (cVar1 == ' ') {
    uVar2 = (uint)DAT_001702bd;
  }
  else {
    uVar2 = (uint)DAT_001702be;
  }
  if (uVar2 != 2) {
    uVar2 = (uint)(uVar2 != 3) + uVar2 * (uVar2 == 3);
  }
  FUN_000a201e(*(undefined4 *)(&DAT_00168d84 + uVar2 * 4),*(undefined2 *)(unaff_gp + -0x5c3c),
               _DAT_febf615e);
  DAT_fef01068 = extraout_var;
  return;
}


// ===== FUNCTION 0x565a8 (FUN_0005657e) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0005657e(void)

{
  int unaff_gp;
  undefined **ppuVar1;
  int iVar2;
  
  if ((DAT_00170223 == -0x80) && (*(char *)(unaff_gp + -0x697e) == '\0')) {
    ppuVar1 = (undefined **)&DAT_00167a60;
  }
  else {
    ppuVar1 = &PTR_DAT_00167a44;
  }
  iVar2 = FUN_000a201e(ppuVar1,*(undefined2 *)(unaff_gp + -0x5c74),
                       *(undefined2 *)(unaff_gp + -0x5c86));
  _DAT_febf615a = FUN_000a1c02(iVar2 + (uint)*(byte *)(unaff_gp + -0x5ec0) * 0x20 + 0x28,0xffff);
  *(short *)(unaff_gp + -0x5ec2) = (short)iVar2;
  return;
}


// ===== FUNCTION 0x57008 (FUN_00056f9e) =====

void FUN_00056f9e(void)

{
  int unaff_gp;
  undefined1 extraout_var;
  
  if (((((DAT_fef010f1 & 1) == 0) || (*(ushort *)(unaff_gp + -0x5c38) < DAT_0017013c)) ||
      (DAT_0017013e < *(ushort *)(unaff_gp + -0x5c38))) ||
     (((*(ushort *)(unaff_gp + -0x5c3e) < DAT_00170140 ||
       (DAT_00170142 < *(ushort *)(unaff_gp + -0x5c3e))) ||
      ((*(ushort *)(unaff_gp + -0x5c86) < (ushort)((ushort)DAT_0017023d * 0x100) ||
       ((ushort)((ushort)DAT_0017023e * 0x100) < *(ushort *)(unaff_gp + -0x5c86))))))) {
    DAT_fef010f1 = DAT_fef010f1 & 0xf7;
  }
  else {
    FUN_000a1fca(&PTR_DAT_00167848);
    DAT_fef010ef = 0;
    DAT_fef010f1 = DAT_fef010f1 | 0xc;
    DAT_fef010f0 = 0xff;
    DAT_febf616e = extraout_var;
  }
  return;
}


// ===== FUNCTION 0x5725e (FUN_0005721a) =====

void FUN_0005721a(void)

{
  ushort uVar1;
  ushort uVar2;
  int unaff_gp;
  undefined *puVar3;
  undefined1 extraout_var;
  int iVar4;
  
  uVar1 = *(ushort *)(unaff_gp + -0x5c86);
  uVar2 = *(ushort *)(unaff_gp + -0x5c5e);
  iVar4 = FUN_00083ae4();
  if (((DAT_00170216 < uVar1) && (uVar1 < DAT_00170218)) && (uVar2 <= DAT_0017021a)) {
    if (iVar4 == 1) {
      puVar3 = &DAT_00169244;
    }
    else {
      puVar3 = &DAT_00169258;
    }
    FUN_000a1fca(puVar3,*(undefined2 *)(unaff_gp + -0x5c6c));
    DAT_febf616f = extraout_var;
  }
  else {
    DAT_febf616f = 0x40;
  }
  return;
}


// ===== FUNCTION 0x577e2 (FUN_00057744) =====

void FUN_00057744(void)

{
  char cVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  char cVar4;
  byte bVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  byte bVar9;
  int unaff_gp;
  undefined *puVar10;
  int iVar11;
  ushort uVar12;
  
  bVar9 = DAT_fef0110e;
  cVar8 = DAT_0017027b;
  cVar7 = DAT_0017027a;
  cVar6 = DAT_00170279;
  bVar5 = DAT_00170278;
  cVar4 = DAT_00170277;
  cVar1 = *(char *)(unaff_gp + -0x5bbe);
  uVar2 = *(undefined2 *)(unaff_gp + -0x5c86);
  uVar3 = *(undefined2 *)(unaff_gp + -0x5c3e);
  if ((*(byte *)(unaff_gp + -0x5e75) & 1) == 0) {
    return;
  }
  DAT_fef01110 = FUN_000a1bf6((uint)((int)(short)(ushort)DAT_fef0110c *
                                    (int)(short)(ushort)DAT_fef0110d) >> 5,0xff);
  uVar12 = (ushort)DAT_fef01110;
  if ((cVar4 == '\x01') || (cVar4 == '\x03')) {
LAB_000577c2:
    puVar10 = &DAT_00167cdc;
  }
  else {
    if (cVar4 != '\x02') {
LAB_000577fe:
      iVar11 = 0;
      goto LAB_00057800;
    }
    if ((cVar1 == cVar6) && ((bVar5 & 4) != 0)) goto LAB_000577c2;
    if ((cVar1 == cVar7) && ((bVar5 & 8) != 0)) {
      puVar10 = &DAT_00167d0c;
    }
    else {
      if ((cVar1 != cVar8) || ((bVar5 & 0x10) == 0)) goto LAB_000577fe;
      puVar10 = &DAT_00167d3c;
    }
  }
  iVar11 = FUN_000a201e(puVar10,uVar3,uVar2);
  iVar11 = iVar11 >> 8;
LAB_00057800:
  DAT_fef0110f = (undefined1)iVar11;
  DAT_fef01111 = FUN_000a1cc2((int)((DAT_febf6174 - 0x40) *
                                   (0x4000 - (int)(short)uVar12 * (int)(short)(ushort)bVar9)) /
                              0x4000 + ((iVar11 + -0x40) *
                                       (int)(short)uVar12 * (int)(short)(ushort)bVar9) / 0x4000 +
                              0x40,0xff,0);
  return;
}


// ===== FUNCTION 0x577f6 (FUN_00057744) =====

void FUN_00057744(void)

{
  char cVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  char cVar4;
  byte bVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  byte bVar9;
  int unaff_gp;
  undefined *puVar10;
  int iVar11;
  ushort uVar12;
  
  bVar9 = DAT_fef0110e;
  cVar8 = DAT_0017027b;
  cVar7 = DAT_0017027a;
  cVar6 = DAT_00170279;
  bVar5 = DAT_00170278;
  cVar4 = DAT_00170277;
  cVar1 = *(char *)(unaff_gp + -0x5bbe);
  uVar2 = *(undefined2 *)(unaff_gp + -0x5c86);
  uVar3 = *(undefined2 *)(unaff_gp + -0x5c3e);
  if ((*(byte *)(unaff_gp + -0x5e75) & 1) == 0) {
    return;
  }
  DAT_fef01110 = FUN_000a1bf6((uint)((int)(short)(ushort)DAT_fef0110c *
                                    (int)(short)(ushort)DAT_fef0110d) >> 5,0xff);
  uVar12 = (ushort)DAT_fef01110;
  if ((cVar4 == '\x01') || (cVar4 == '\x03')) {
LAB_000577c2:
    puVar10 = &DAT_00167cdc;
  }
  else {
    if (cVar4 != '\x02') {
LAB_000577fe:
      iVar11 = 0;
      goto LAB_00057800;
    }
    if ((cVar1 == cVar6) && ((bVar5 & 4) != 0)) goto LAB_000577c2;
    if ((cVar1 == cVar7) && ((bVar5 & 8) != 0)) {
      puVar10 = &DAT_00167d0c;
    }
    else {
      if ((cVar1 != cVar8) || ((bVar5 & 0x10) == 0)) goto LAB_000577fe;
      puVar10 = &DAT_00167d3c;
    }
  }
  iVar11 = FUN_000a201e(puVar10,uVar3,uVar2);
  iVar11 = iVar11 >> 8;
LAB_00057800:
  DAT_fef0110f = (undefined1)iVar11;
  DAT_fef01111 = FUN_000a1cc2((int)((DAT_febf6174 - 0x40) *
                                   (0x4000 - (int)(short)uVar12 * (int)(short)(ushort)bVar9)) /
                              0x4000 + ((iVar11 + -0x40) *
                                       (int)(short)uVar12 * (int)(short)(ushort)bVar9) / 0x4000 +
                              0x40,0xff,0);
  return;
}


// ===== FUNCTION 0x58e98 (FUN_00058e68) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00058e68(void)

{
  char cVar1;
  int unaff_gp;
  undefined **ppuVar2;
  undefined2 uVar3;
  
  cVar1 = *(char *)(unaff_gp + -0x5bbe);
  if (cVar1 == '\x02') {
    ppuVar2 = &PTR_DAT_00167898;
  }
  else if (cVar1 == '\x04') {
    ppuVar2 = &PTR_DAT_001678c0;
  }
  else if (cVar1 == '\b') {
    ppuVar2 = &PTR_DAT_001678e8;
  }
  else if (cVar1 == '\x10') {
    ppuVar2 = &PTR_DAT_00167910;
  }
  else if (cVar1 == ' ') {
    ppuVar2 = &PTR_DAT_00167938;
  }
  else {
    ppuVar2 = &PTR_DAT_00167960;
  }
  uVar3 = FUN_000a1fca(ppuVar2,_DAT_febf615e);
  *(undefined2 *)(unaff_gp + -0x5e5e) = uVar3;
  return;
}


// ===== FUNCTION 0x58efa (FUN_00058eca) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00058eca(void)

{
  char cVar1;
  int unaff_gp;
  undefined *puVar2;
  undefined2 uVar3;
  
  cVar1 = *(char *)(unaff_gp + -0x5bbe);
  if (cVar1 == '\x02') {
    puVar2 = &DAT_001678ac;
  }
  else if (cVar1 == '\x04') {
    puVar2 = &DAT_001678d4;
  }
  else if (cVar1 == '\b') {
    puVar2 = &DAT_001678fc;
  }
  else if (cVar1 == '\x10') {
    puVar2 = &DAT_00167924;
  }
  else if (cVar1 == ' ') {
    puVar2 = &DAT_0016794c;
  }
  else {
    puVar2 = &DAT_00167974;
  }
  uVar3 = FUN_000a1fca(puVar2,_DAT_febf615e);
  *(undefined2 *)(unaff_gp + -0x5e5c) = uVar3;
  return;
}


// ===== FUNCTION 0x5967a (FUN_00059634) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00059634(void)

{
  char cVar1;
  undefined2 uVar2;
  int unaff_gp;
  undefined *puVar3;
  undefined1 extraout_var;
  int iVar4;
  
  cVar1 = *(char *)(unaff_gp + -0x5bbe);
  uVar2 = *(undefined2 *)(unaff_gp + -0x5c3a);
  iVar4 = FUN_00085dbe();
  if ((cVar1 == '\x01') || ((iVar4 == 1 && (DAT_0017025f == -0x80)))) {
    puVar3 = &DAT_00167a7c;
  }
  else if (DAT_febf6173 == '\x03') {
    puVar3 = &DAT_00167ad0;
  }
  else if (DAT_febf6173 == '\x02') {
    puVar3 = &DAT_00167ab4;
  }
  else {
    puVar3 = &DAT_00167a98;
  }
  FUN_000a201e(puVar3,uVar2,_DAT_febf615e);
  DAT_febf617b = extraout_var;
  return;
}


// ===== FUNCTION 0x59686 (FUN_00059634) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00059634(void)

{
  char cVar1;
  undefined2 uVar2;
  int unaff_gp;
  undefined *puVar3;
  undefined1 extraout_var;
  int iVar4;
  
  cVar1 = *(char *)(unaff_gp + -0x5bbe);
  uVar2 = *(undefined2 *)(unaff_gp + -0x5c3a);
  iVar4 = FUN_00085dbe();
  if ((cVar1 == '\x01') || ((iVar4 == 1 && (DAT_0017025f == -0x80)))) {
    puVar3 = &DAT_00167a7c;
  }
  else if (DAT_febf6173 == '\x03') {
    puVar3 = &DAT_00167ad0;
  }
  else if (DAT_febf6173 == '\x02') {
    puVar3 = &DAT_00167ab4;
  }
  else {
    puVar3 = &DAT_00167a98;
  }
  FUN_000a201e(puVar3,uVar2,_DAT_febf615e);
  DAT_febf617b = extraout_var;
  return;
}


// ===== FUNCTION 0x5968e (FUN_00059634) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00059634(void)

{
  char cVar1;
  undefined2 uVar2;
  int unaff_gp;
  undefined *puVar3;
  undefined1 extraout_var;
  int iVar4;
  
  cVar1 = *(char *)(unaff_gp + -0x5bbe);
  uVar2 = *(undefined2 *)(unaff_gp + -0x5c3a);
  iVar4 = FUN_00085dbe();
  if ((cVar1 == '\x01') || ((iVar4 == 1 && (DAT_0017025f == -0x80)))) {
    puVar3 = &DAT_00167a7c;
  }
  else if (DAT_febf6173 == '\x03') {
    puVar3 = &DAT_00167ad0;
  }
  else if (DAT_febf6173 == '\x02') {
    puVar3 = &DAT_00167ab4;
  }
  else {
    puVar3 = &DAT_00167a98;
  }
  FUN_000a201e(puVar3,uVar2,_DAT_febf615e);
  DAT_febf617b = extraout_var;
  return;
}


// ===== FUNCTION 0x596ca (FUN_000596a6) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000596a6(void)

{
  int unaff_gp;
  undefined *puVar1;
  undefined1 extraout_var;
  
  if (*(char *)(unaff_gp + -0x5e53) == '\x03') {
    puVar1 = &DAT_00167b5c;
  }
  else if (*(char *)(unaff_gp + -0x5e53) == '\x02') {
    puVar1 = &DAT_00167b40;
  }
  else {
    puVar1 = &DAT_00167b24;
  }
  FUN_000a201e(puVar1,*(undefined2 *)(unaff_gp + -0x5c3a),_DAT_febf615e);
  *(undefined1 *)(unaff_gp + -0x5e58) = extraout_var;
  return;
}


// ===== FUNCTION 0x596d2 (FUN_000596a6) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000596a6(void)

{
  int unaff_gp;
  undefined *puVar1;
  undefined1 extraout_var;
  
  if (*(char *)(unaff_gp + -0x5e53) == '\x03') {
    puVar1 = &DAT_00167b5c;
  }
  else if (*(char *)(unaff_gp + -0x5e53) == '\x02') {
    puVar1 = &DAT_00167b40;
  }
  else {
    puVar1 = &DAT_00167b24;
  }
  FUN_000a201e(puVar1,*(undefined2 *)(unaff_gp + -0x5c3a),_DAT_febf615e);
  *(undefined1 *)(unaff_gp + -0x5e58) = extraout_var;
  return;
}


// ===== FUNCTION 0x59706 (FUN_000596e6) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000596e6(void)

{
  int unaff_gp;
  undefined *puVar1;
  undefined1 extraout_var;
  int iVar2;
  
  iVar2 = FUN_00083ae4();
  if (iVar2 == 1) {
    puVar1 = &DAT_00167aec;
  }
  else {
    puVar1 = &DAT_00167b08;
  }
  FUN_000a201e(puVar1,*(undefined2 *)(unaff_gp + -0x5c3a),_DAT_febf615e);
  *(undefined1 *)(unaff_gp + -0x5e57) = extraout_var;
  return;
}


// ===== FUNCTION 0x59746 (FUN_0005971a) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0005971a(void)

{
  undefined2 uVar1;
  undefined2 uVar2;
  int unaff_gp;
  undefined *puVar3;
  undefined1 extraout_var;
  int iVar4;
  
  uVar2 = _DAT_febf615e;
  uVar1 = *(undefined2 *)(unaff_gp + -0x5c3a);
  iVar4 = FUN_00083ae4();
  if (iVar4 == 1) {
    puVar3 = &DAT_00167b78;
  }
  else if (*(char *)(unaff_gp + -0x5e49) == '\x03') {
    puVar3 = &DAT_00167bcc;
  }
  else if (*(char *)(unaff_gp + -0x5e49) == '\x02') {
    puVar3 = &DAT_00167bb0;
  }
  else {
    puVar3 = &DAT_00167b94;
  }
  FUN_000a201e(puVar3,uVar1,uVar2);
  *(undefined1 *)(unaff_gp + -0x5e56) = extraout_var;
  return;
}


// ===== FUNCTION 0x59752 (FUN_0005971a) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0005971a(void)

{
  undefined2 uVar1;
  undefined2 uVar2;
  int unaff_gp;
  undefined *puVar3;
  undefined1 extraout_var;
  int iVar4;
  
  uVar2 = _DAT_febf615e;
  uVar1 = *(undefined2 *)(unaff_gp + -0x5c3a);
  iVar4 = FUN_00083ae4();
  if (iVar4 == 1) {
    puVar3 = &DAT_00167b78;
  }
  else if (*(char *)(unaff_gp + -0x5e49) == '\x03') {
    puVar3 = &DAT_00167bcc;
  }
  else if (*(char *)(unaff_gp + -0x5e49) == '\x02') {
    puVar3 = &DAT_00167bb0;
  }
  else {
    puVar3 = &DAT_00167b94;
  }
  FUN_000a201e(puVar3,uVar1,uVar2);
  *(undefined1 *)(unaff_gp + -0x5e56) = extraout_var;
  return;
}


// ===== FUNCTION 0x5975a (FUN_0005971a) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0005971a(void)

{
  undefined2 uVar1;
  undefined2 uVar2;
  int unaff_gp;
  undefined *puVar3;
  undefined1 extraout_var;
  int iVar4;
  
  uVar2 = _DAT_febf615e;
  uVar1 = *(undefined2 *)(unaff_gp + -0x5c3a);
  iVar4 = FUN_00083ae4();
  if (iVar4 == 1) {
    puVar3 = &DAT_00167b78;
  }
  else if (*(char *)(unaff_gp + -0x5e49) == '\x03') {
    puVar3 = &DAT_00167bcc;
  }
  else if (*(char *)(unaff_gp + -0x5e49) == '\x02') {
    puVar3 = &DAT_00167bb0;
  }
  else {
    puVar3 = &DAT_00167b94;
  }
  FUN_000a201e(puVar3,uVar1,uVar2);
  *(undefined1 *)(unaff_gp + -0x5e56) = extraout_var;
  return;
}

