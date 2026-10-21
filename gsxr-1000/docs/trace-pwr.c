
// ===== FUNCTION 0x8be2c (FUN_0008be2c) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0008be2c(void)

{
  _DAT_fef02e0c = (&PTR_DAT_00192ba8)[(uint)DAT_fef02e51 * 6 + (uint)DAT_fef0267c];
  _DAT_fef02e26 = FUN_000a201e(_DAT_fef02e0c,_DAT_fef02e44,_DAT_fef02e46);
  return;
}


// ===== FUNCTION 0x8c0de (FUN_0008c0de) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0008c0de(ushort param_1)

{
  bool bVar1;
  char cVar2;
  int iVar3;
  
  cVar2 = DAT_fef005f6;
  iVar3 = FUN_00029e54();
  if ((param_1 < _DAT_fef02e32) && (cVar2 == '\x01')) {
    if (iVar3 == 1) {
      bVar1 = -1 < (int)((uint)DAT_fef02e56 << 0x1d);
      _DAT_fef02e36 = DAT_00192c6c * (ushort)bVar1 + _DAT_fef02e36 * (ushort)!bVar1;
    }
  }
  else {
    _DAT_fef02e36 = 0;
  }
  return;
}


// ===== FUNCTION 0x8c2d6 (FUN_0008c2d6) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0008c2d6(void)

{
  DAT_fef02e4d = DAT_00192cf5;
  _DAT_fef02e24 = DAT_00192c60;
  switch(DAT_fef02e4c) {
  case 0:
    if ((DAT_fef02e56 & 0x20) != 0) {
      DAT_fef02e4d = DAT_00192cf7;
      _DAT_fef02e24 = DAT_00192c64;
    }
    break;
  case 1:
    DAT_fef02e4d = DAT_00192cf6;
    _DAT_fef02e24 = DAT_00192c62;
    break;
  case 2:
    DAT_fef02e4d = DAT_00192cf8;
    _DAT_fef02e24 = DAT_00192c66;
    break;
  case 3:
    DAT_fef02e4d = DAT_00192cf9;
    _DAT_fef02e24 = DAT_00192c68;
    break;
  case 4:
    DAT_fef02e4d = DAT_00192cfa;
    _DAT_fef02e24 = DAT_00192c6a;
  }
  return;
}


// ===== FUNCTION 0x8c58e (FUN_0008c58e) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint FUN_0008c58e(void)

{
  byte bVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  byte bVar5;
  undefined2 uVar6;
  ushort uVar7;
  ushort uVar8;
  ushort uVar9;
  char cVar10;
  ushort uVar11;
  char cVar12;
  int unaff_gp;
  undefined2 uVar13;
  char cVar14;
  undefined2 uVar15;
  int iVar16;
  uint uVar17;
  uint uVar18;
  int iVar19;
  uint uVar20;
  
  cVar10 = DAT_fef005f8;
  uVar20 = (uint)_DAT_fef02e16;
  uVar2 = *(ushort *)(unaff_gp + -0x5e44);
  uVar3 = *(ushort *)(unaff_gp + -0x5ad4);
  uVar18 = (uint)_DAT_fef02e14;
  iVar16 = FUN_0002eeac();
  cVar14 = FUN_0002eec8();
  uVar4 = *(ushort *)(unaff_gp + -0x5c10);
  uVar15 = FUN_000a1c02();
  cVar12 = DAT_fef02e4c;
  uVar11 = _DAT_fef02622;
  uVar9 = DAT_00192c5a;
  uVar13 = DAT_00192c58;
  uVar8 = DAT_00192c56;
  uVar7 = DAT_00192c54;
  uVar6 = DAT_00154d8a;
  uVar17 = (uint)DAT_fef072c4;
  bVar5 = DAT_fef072c4 & 1;
  iVar19 = uVar2 + uVar20;
  bVar1 = *(byte *)(unaff_gp + -0x5b67);
  if (DAT_00192cf4 == -0x80) {
    uVar18 = FUN_000a1cc2(uVar18 * 2 + (uint)uVar3 + iVar19 + -0x10000,0xffff,0);
    uVar18 = uVar18 & 0xffff;
    uVar17 = uVar18;
    goto LAB_0008c6ee;
  }
  uVar18 = FUN_000a1c02((uint)uVar3 + iVar19);
  uVar18 = uVar18 & 0xffff;
  if (((bVar1 & 1) == 1) && (bVar5 == 1)) {
    if ((int)(uVar17 << 0x1d) < 0) {
      uVar17 = (uint)uVar7;
      goto LAB_0008c6ee;
    }
    if ((int)(uVar17 << 0x1e) < 0) {
      uVar17 = (uint)uVar8;
      goto LAB_0008c6ee;
    }
  }
  uVar17 = uVar18;
  if (cVar12 == '\x03') goto LAB_0008c6ee;
  if ((cVar10 != '\t') && (uVar13 = uVar6, cVar10 != '\b')) {
    if ((uVar11 <= uVar9) && (uVar4 <= uVar9)) goto LAB_0008c6ee;
    if (iVar16 == 1) {
      uVar17 = FUN_000a1b74(uVar15,uVar18);
      goto LAB_0008c6ee;
    }
    uVar13 = uVar15;
    if (cVar14 != '\x01') goto LAB_0008c6ee;
  }
  uVar17 = FUN_000a1bf6(uVar13,uVar18);
LAB_0008c6ee:
  _DAT_fef02d7a = (short)uVar18;
  return uVar17;
}


// ===== FUNCTION 0x8c6fa (FUN_0008c6fa) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0008c6fa(void)

{
  ushort uVar1;
  byte bVar2;
  char cVar3;
  byte bVar4;
  int unaff_gp;
  byte bVar5;
  byte bVar6;
  ushort uVar7;
  undefined2 uVar8;
  
  bVar5 = DAT_fef02e53;
  bVar4 = DAT_fef02e52;
  cVar3 = DAT_febf653c;
  bVar2 = DAT_00192cf3;
  uVar1 = DAT_00192c52;
  uVar8 = DAT_00192c50;
  bVar6 = *(byte *)(unaff_gp + -0x5d29) & 4;
  if ((*(byte *)(unaff_gp + -0x5d29) & 4) == 0) {
    FUN_0008c9dc(bVar6);
    uVar8 = FUN_0008c58e();
    bVar5 = bVar6;
  }
  else {
    if (DAT_fef02e52 < DAT_00192cf2) {
      uVar8 = FUN_0008c58e();
    }
    else {
      uVar7 = FUN_000a1b5c(_DAT_febf6536 - 0x8000);
      if (uVar1 < uVar7) {
        bVar5 = 0;
      }
      else {
        if (bVar2 <= bVar5) {
          FUN_0008c9dc(1);
        }
        bVar5 = FUN_000a1cd2(bVar5,1);
      }
    }
    if (cVar3 == '\t') {
      FUN_0008c9dc(1);
    }
    bVar6 = FUN_000a1cd2(bVar4,1);
  }
  DAT_fef02e52 = bVar6;
  DAT_fef02e53 = bVar5;
  _DAT_fef02e3e = uVar8;
  return;
}


// ===== FUNCTION 0x8c7b0 (FUN_0008c7b0) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0008c7b0(void)

{
  ushort uVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = (uint)DAT_00192c5e;
  iVar3 = (uint)_DAT_fef02d7c - (uint)_DAT_fef02e3e;
  uVar1 = _DAT_fef02e3e;
  if (((uint)_DAT_fef02e3e < (uint)DAT_00192c5c) &&
     ((int)(iVar3 - uVar2) < 0 == (iVar3 < 0 && -1 < (int)(iVar3 - uVar2)))) {
    uVar1 = FUN_000a1cc2(_DAT_fef02d7c - uVar2,0xffff,0);
  }
  _DAT_fef02d7c = uVar1;
  return;
}


// ===== FUNCTION 0x8c7fa (FUN_0008c7fa) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0008c7fa(void)

{
  int unaff_gp;
  undefined2 uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  
  iVar2 = FUN_00036d6e();
  iVar3 = FUN_0002c790();
  uVar1 = DAT_00192c74;
  if (iVar2 == 0) {
    uVar6 = (uint)DAT_00192c72;
    uVar5 = (uint)_DAT_fef02e40;
    if (iVar3 == 1) {
      uVar4 = FUN_000a1fca(&PTR_DAT_001746d4,*(undefined1 *)(unaff_gp + -0x5bbe));
      uVar1 = FUN_000a1ba0(uVar5 - uVar6,uVar4);
    }
    else {
      uVar4 = FUN_000a1fca(&PTR_DAT_001746c0,*(undefined2 *)(unaff_gp + -0x5c84));
      _DAT_fef02e4a = (undefined2)uVar4;
      uVar1 = FUN_000a1c02(uVar6 + uVar5,uVar4);
    }
  }
  _DAT_fef02e40 = uVar1;
  return;
}


// ===== FUNCTION 0x8c86e (FUN_0008c86e) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0008c86e(void)

{
  byte bVar1;
  bool bVar2;
  ushort uVar3;
  ushort uVar4;
  int iVar5;
  int unaff_gp;
  char cVar6;
  undefined1 uVar7;
  undefined2 uVar8;
  int iVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  uint uVar17;
  int iVar18;
  
  uVar8 = *(undefined2 *)(unaff_gp + -0x5c84);
  uVar15 = (uint)DAT_fef02e58;
  uVar13 = (uint)_DAT_fef005be;
  uVar14 = (uint)_DAT_fef005b8;
  uVar17 = (uint)_DAT_fef005c0;
  cVar6 = FUN_0002ff2a();
  uVar3 = _DAT_fef005f4;
  uVar4 = DAT_00192c70;
  uVar16 = (uint)DAT_00192cfb;
  uVar12 = (uint)DAT_00192c54;
  uVar11 = (uint)DAT_00192c56;
  iVar9 = FUN_000a1fca(&PTR_DAT_001746c0,uVar8);
  uVar10 = (uint)_DAT_fef02d7c;
  bVar2 = (int)(uVar11 - uVar17) < 0;
  uVar11 = uVar17 * (bVar2 || uVar11 == uVar17) + uVar11 * (!bVar2 && uVar11 != uVar17);
  bVar2 = (int)(uVar11 - uVar10) < 0;
  iVar18 = uVar10 * (bVar2 || uVar11 == uVar10) + uVar11 * (!bVar2 && uVar11 != uVar10);
  uVar11 = (uint)_DAT_fef02e40;
  bVar1 = -(char)(iVar9 >> 0x1f);
  bVar2 = (int)(uVar12 - iVar9) < 0 == (bVar1 != 0 && bVar1 == (byte)(uVar12 - iVar9 >> 0x1f));
  iVar5 = iVar9 * (uint)bVar2 + uVar12 * !bVar2;
  bVar2 = (int)(iVar5 - uVar11) < 0 == (iVar5 < 0 && -1 < (int)(iVar5 - uVar11));
  iVar5 = uVar11 * bVar2 + iVar5 * (uint)!bVar2;
  bVar2 = (int)(iVar5 - uVar13) < 0 == (iVar5 < 0 && -1 < (int)(iVar5 - uVar13));
  iVar5 = uVar13 * bVar2 + iVar5 * (uint)!bVar2;
  bVar2 = (int)(iVar5 - uVar14) < 0 == (iVar5 < 0 && -1 < (int)(iVar5 - uVar14));
  iVar5 = uVar14 * bVar2 + iVar5 * (uint)!bVar2;
  _DAT_fef02e4a = (undefined2)iVar9;
  bVar2 = iVar5 - iVar18 < 0 == (iVar5 < 0 && -1 < iVar5 - iVar18);
  iVar5 = iVar18 * (uint)bVar2 + iVar5 * (uint)!bVar2;
  if (cVar6 != '\0') {
    uVar3 = uVar4;
  }
  uVar11 = (uint)uVar3;
  bVar1 = -(char)(iVar5 >> 0x1f);
  bVar2 = (int)(uVar11 - iVar5) < 0 == (bVar1 != 0 && bVar1 == (byte)(uVar11 - iVar5 >> 0x1f));
  uVar10 = iVar5 * (uint)bVar2 + uVar11 * !bVar2;
  uVar11 = (uint)(10 < uVar16) * 10 + uVar16 * (uVar16 < 0xb);
  uVar3 = (ushort)uVar10;
  if (uVar15 == 0) {
    _DAT_fef02e42 = uVar3;
  }
  uVar12 = uVar10;
  if (uVar11 != 0) {
    uVar4 = _DAT_fef02e42;
    if (uVar11 <= uVar15) {
      uVar4 = *(ushort *)((uint)DAT_fef02e57 * 2 + -0x10fd1a6);
    }
    uVar12 = (uint)DAT_fef02e57;
    *(ushort *)(uVar12 * 2 + -0x10fd1a6) = uVar3;
    uVar13 = FUN_000a1cd2(uVar12,1);
    DAT_fef02e57 = (byte)uVar13;
    uVar12 = (uint)uVar4;
    if (uVar11 <= uVar13) {
      DAT_fef02e57 = 0;
    }
  }
  uVar7 = FUN_000a1cd2(uVar15,1);
  uVar8 = FUN_000a1cc2((int)(uVar10 - uVar12) / 2 + 0x8000,0xffff,0);
  *(ushort *)(unaff_gp + -0x5ad8) = uVar3;
  _DAT_fef02e3c = (undefined2)uVar12;
  *(undefined2 *)(unaff_gp + -0x5ad6) = uVar8;
  DAT_fef02e58 = uVar7;
  return;
}


// ===== FUNCTION 0x8b388 (FUN_0008b388) =====

void FUN_0008b388(void)

{
  int unaff_gp;
  
  if ((((DAT_febf653c == '\0') && (DAT_00192c7c <= *(ushort *)(unaff_gp + -0x5c46))) &&
      (DAT_fef02dee == '\0')) && ((*(byte *)(unaff_gp + -0x5ac1) & 1) == 0)) {
    DAT_febf653c = '\x01';
  }
  if ((DAT_febf653c == '\x01') && ((*(byte *)(unaff_gp + -0x5ac1) & 0x80) != 0)) {
    DAT_febf653c = '\x02';
    *(byte *)(unaff_gp + -0x5ac1) = *(byte *)(unaff_gp + -0x5ac1) & 0x7f;
  }
  if ((DAT_febf653c == '\x02') && ((*(byte *)(unaff_gp + -0x5ac1) & 0x20) != 0)) {
    DAT_febf653c = '\x03';
    *(byte *)(unaff_gp + -0x5ac1) = *(byte *)(unaff_gp + -0x5ac1) & 0xdf;
  }
  if (DAT_febf653c == '\x03') {
    if (((*(byte *)(unaff_gp + -0x5ac0) & 8) == 0) && ((*(byte *)(unaff_gp + -0x5ac1) & 0x40) != 0))
    {
      DAT_febf653c = '\x04';
      *(byte *)(unaff_gp + -0x5ac1) = *(byte *)(unaff_gp + -0x5ac1) & 0xbf;
    }
    if (((DAT_febf653c == '\x03') && ((*(byte *)(unaff_gp + -0x5ac0) & 8) != 0)) &&
       ((*(byte *)(unaff_gp + -0x5ac1) & 0x40) != 0)) {
      *(byte *)(unaff_gp + -0x5ac1) = *(byte *)(unaff_gp + -0x5ac1) & 0xbf;
      DAT_febf653c = '\b';
      *(byte *)(unaff_gp + -0x5ac0) = *(byte *)(unaff_gp + -0x5ac0) & 0xf7;
    }
  }
  return;
}


// ===== FUNCTION 0x8bdc8 (FUN_0008bdc8) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0008bdc8(void)

{
  int unaff_gp;
  int iVar1;
  
  _DAT_fef02e44 = *(undefined2 *)(unaff_gp + -0x5c52);
  _DAT_fef02e46 = *(undefined2 *)(unaff_gp + -0x5c84);
  iVar1 = FUN_00085dbe();
  iVar1 = iVar1 * (uint)(iVar1 == 1) + (uint)*(byte *)(unaff_gp + -0x5bbe) * (uint)(iVar1 != 1);
  if (iVar1 == 1) {
    DAT_fef02e51 = 0;
  }
  else if (iVar1 == 2) {
    DAT_fef02e51 = 1;
  }
  else if (iVar1 == 4) {
    DAT_fef02e51 = 2;
  }
  else if (iVar1 == 8) {
    DAT_fef02e51 = 3;
  }
  else if (iVar1 == 0x10) {
    DAT_fef02e51 = 4;
  }
  else if (iVar1 == 0x20) {
    DAT_fef02e51 = 5;
  }
  else {
    DAT_fef02e51 = 6;
  }
  return;
}

