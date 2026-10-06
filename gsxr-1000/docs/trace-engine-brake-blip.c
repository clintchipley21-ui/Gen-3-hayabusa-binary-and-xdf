
// ===== FUNCTION 0x28ca6 (FUN_00028ca6) =====

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


// ===== FUNCTION 0x28c06 (FUN_00028bf0) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00028bf0(void)

{
  byte bVar1;
  int unaff_gp;
  int iVar2;
  
  bVar1 = DAT_00154e15;
  if (((((*(char *)(unaff_gp + -0x5ba6) == '\0') || ((DAT_fef00524 & 1) == 0)) ||
       (DAT_00154d00 < *(ushort *)(unaff_gp + -0x5c52))) ||
      (((_DAT_fef02622 <= DAT_00154d02 && (*(ushort *)(unaff_gp + -0x5c10) <= DAT_00154d02)) ||
       ((iVar2 = FUN_00037122(), iVar2 != 0 ||
        ((iVar2 = FUN_00037106(), iVar2 != 0 || (iVar2 = FUN_00036b54(), iVar2 != 0)))))))) ||
     ((iVar2 = FUN_00036b70(), iVar2 != 0 ||
      ((((iVar2 = FUN_00036d6e(), iVar2 != 0 || (*(char *)(unaff_gp + -0x5bbe) == '\x01')) ||
        (iVar2 = FUN_00085dbe(), iVar2 != 0)) || (iVar2 = FUN_0002eeac(), iVar2 != 0)))))) {
    FUN_00028e90(0);
    DAT_fef00525 = 0;
  }
  else {
    if (bVar1 <= DAT_fef00525) {
      FUN_00028e90(1);
    }
    DAT_fef00525 = FUN_000a1cd2(DAT_fef00525,1);
  }
  return;
}


// ===== FUNCTION 0x28d9a (FUN_00028ca6) =====

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


// ===== FUNCTION 0x28e2a (FUN_00028de0) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00028de0(void)

{
  char cVar1;
  char cVar2;
  int unaff_gp;
  byte bVar3;
  undefined2 uVar4;
  int iVar5;
  
  cVar2 = DAT_00154e17;
  cVar1 = *(char *)(unaff_gp + -0x5bbe);
  iVar5 = FUN_0002963c();
  bVar3 = DAT_fef00526;
  if (cVar2 == '\x01') {
    FUN_00028b84();
    FUN_00028bf0();
    FUN_00028ca6();
    FUN_00028da0();
  }
  else {
    if ((cVar1 == '\x01') || (iVar5 == 1)) {
      uVar4 = 0;
      if (DAT_fef00526 < DAT_00154e16) {
        uVar4 = FUN_000a201e(&DAT_00151210,*(undefined2 *)(unaff_gp + -0x5c86),
                             *(undefined1 *)(unaff_gp + -0x5ba6));
      }
      bVar3 = FUN_000a1cd2(bVar3,1);
    }
    else {
      uVar4 = FUN_000a201e(&DAT_00151210,*(undefined2 *)(unaff_gp + -0x5c86),
                           *(undefined1 *)(unaff_gp + -0x5ba6));
      bVar3 = 0;
    }
    FUN_00028e90(0);
    DAT_febf5e8e = 0x40;
    FUN_00028eac(0);
    DAT_fef00526 = bVar3;
    _DAT_fef005c0 = uVar4;
  }
  return;
}


// ===== FUNCTION 0x2a2ba (FUN_0002a2ba) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0002a2ba(void)

{
  bool bVar1;
  char cVar2;
  ushort uVar3;
  ushort uVar4;
  bool bVar5;
  ushort uVar6;
  ushort uVar7;
  char cVar8;
  char cVar9;
  ushort uVar10;
  ushort uVar11;
  ushort uVar12;
  ushort uVar13;
  char cVar14;
  int unaff_gp;
  undefined *puVar15;
  char cVar16;
  char cVar17;
  ushort uVar18;
  ushort uVar19;
  ushort uVar20;
  undefined2 uVar21;
  uint uVar22;
  undefined *puVar23;
  byte bVar24;
  uint uVar25;
  uint uVar26;
  int iVar27;
  uint uVar28;
  uint uVar29;
  int iVar30;
  uint uVar31;
  char cStack_49;
  
  cVar14 = DAT_fef0267f;
  uVar13 = _DAT_fef00584;
  uVar12 = _DAT_fef0057e;
  uVar11 = _DAT_fef00578;
  uVar10 = _DAT_fef00568;
  cVar9 = DAT_00154dd5;
  cVar8 = DAT_00154dd4;
  uVar7 = DAT_00154c7e;
  uVar6 = DAT_00154c7a;
  uVar29 = (uint)DAT_fef005a2;
  cVar2 = *(char *)(unaff_gp + -0x5bbe);
  uVar3 = *(ushort *)(unaff_gp + -0x5c86);
  uVar4 = *(ushort *)(unaff_gp + -0x5c60);
  uVar31 = (uint)DAT_fef005a2;
  uVar25 = (uint)DAT_001559ba;
  uVar26 = (uint)DAT_001559bc;
  uVar28 = (uint)_DAT_fef02630;
  cVar16 = FUN_00085dbe();
  cStack_49 = FUN_00029efc();
  bVar24 = DAT_fef005b1 & 1;
  iVar27 = -((int)((uint)DAT_fef005a2 << 0x1b) >> 0x1f);
  cVar17 = FUN_00029f18();
  bVar1 = false;
  bVar5 = false;
  uVar18 = FUN_000a1fca(&DAT_00150980,cVar2);
  uVar19 = FUN_000a1fca(&DAT_00150994,cVar2);
  if (cVar14 == '\x02') {
    puVar15 = &DAT_00150ed8;
    puVar23 = &LAB_00150f48;
  }
  else {
    puVar15 = &DAT_00150ea0;
    puVar23 = &DAT_00150f10;
  }
  uVar20 = FUN_000a201e(puVar15,uVar3,cVar2);
  uVar22 = FUN_000a201e(puVar23,uVar3,cVar2);
  _DAT_fef0056c = (undefined2)uVar22;
  _DAT_fef0056a = uVar20;
  if (uVar10 <= uVar4) {
    if (cVar8 == -0x80) {
      if (((uVar26 * 0x40 <= uVar28) && (uVar28 <= uVar25 * 0x40)) &&
         ((uVar28 <= uVar20 || (uVar22 <= uVar28)))) {
        bVar1 = uVar6 <= uVar12;
        uVar21 = FUN_000a1cf6(uVar12,1);
        goto LAB_0002a424;
      }
    }
    else if (uVar11 < uVar10) {
      bVar5 = true;
    }
  }
  uVar21 = 0;
LAB_0002a424:
  if (((bVar5) || (bVar1)) && ((cVar9 != -0x80 || (cVar16 == '\0')))) {
    iVar30 = 1;
    _DAT_fef00584 = 0;
  }
  else {
    iVar30 = -((int)(uVar29 << 0x1c) >> 0x1f) * (uint)(uVar13 < uVar7);
    _DAT_fef00584 = FUN_000a1cf6(uVar13,1);
  }
  if (iVar30 == 1) {
    DAT_fef005a2 = DAT_fef005a2 | 8;
    if ((int)(uVar31 << 0x1e) < 0) {
      if ((((uVar18 < uVar3) && (uVar3 < uVar19)) && (cVar2 != '\x01')) && (cVar2 != '@')) {
        cStack_49 = '\x01';
      }
      else if ((bVar24 == 0) && (cStack_49 == '\0')) {
        iVar27 = (uint)(cVar17 == '\0') + iVar27 * (uint)(cVar17 != '\0');
      }
    }
  }
  else {
    DAT_fef005a2 = DAT_fef005a2 & 0xf7;
  }
  _DAT_fef0057e = uVar21;
  FUN_00029f06(cStack_49);
  if (iVar27 == 1) {
    DAT_fef005a2 = DAT_fef005a2 | 0x10;
  }
  else {
    DAT_fef005a2 = DAT_fef005a2 & 0xef;
  }
  return;
}

