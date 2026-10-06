
// ===== FUNCTION 0x2862a (FUN_0002862a) =====

void FUN_0002862a(void)

{
  int unaff_gp;
  undefined2 uVar1;
  undefined4 uVar2;
  
  uVar1 = *(undefined2 *)(unaff_gp + -0x5c08);
  uVar2 = FUN_000a1fca(&PTR_DAT_001511c4,uVar1);
  uVar1 = FUN_000a1cf6(uVar1,uVar2);
  *(undefined2 *)(unaff_gp + -0x619a) = uVar1;
  return;
}


// ===== FUNCTION 0x286b6 (FUN_000286b6) =====

void FUN_000286b6(void)

{
  int unaff_gp;
  undefined2 uVar1;
  int iVar2;
  
  uVar1 = FUN_000a1c02();
  iVar2 = FUN_000282b4();
  if ((iVar2 == 0) && ((*(byte *)(unaff_gp + -0x6196) & 8) != 0)) {
    iVar2 = FUN_000a201e(&DAT_001511d8,uVar1,*(undefined2 *)(unaff_gp + -0x6198));
    *(int *)(unaff_gp + -0x61a0) = iVar2 << 8;
  }
  return;
}


// ===== FUNCTION 0x2888c (FUN_0002885e) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0002885e(void)

{
  ushort uVar1;
  int iVar2;
  
  uVar1 = DAT_00154cf6;
  iVar2 = FUN_00028378();
  if ((iVar2 == 1) && (iVar2 = FUN_00083236(), iVar2 == 0)) {
    if (uVar1 <= _DAT_fef0031a) {
      FUN_00028382(0);
    }
    _DAT_fef0031a = FUN_000a1cf6(_DAT_fef0031a,1);
  }
  else {
    _DAT_fef0031a = 0;
  }
  return;
}


// ===== FUNCTION 0x28700 (FUN_000286f4) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000286f4(void)

{
  bool bVar1;
  uint uVar2;
  int unaff_gp;
  int iVar3;
  uint uVar4;
  
  iVar3 = FUN_000282b4();
  if ((iVar3 == 0) && ((*(byte *)(unaff_gp + -0x6196) & 8) != 0)) {
    *(byte *)(unaff_gp + -0x6196) = *(byte *)(unaff_gp + -0x6196) | 2;
  }
  uVar2 = _DAT_fef0030c;
  bVar1 = (*(byte *)(unaff_gp + -0x6196) & 2) != 0;
  uVar4 = (uint)bVar1;
  if (bVar1) {
    if (*(uint *)(unaff_gp + -0x61a0) <= _DAT_fef0030c) {
      *(undefined4 *)(unaff_gp + -0x61a4) = 0;
      *(byte *)(unaff_gp + -0x6196) = *(byte *)(unaff_gp + -0x6196) & 0xfd;
    }
    uVar4 = uVar2 + 1;
    if (uVar2 == 0xffffffff) {
      return;
    }
  }
  _DAT_fef0030c = uVar4;
  return;
}


// ===== FUNCTION 0x2c8fe (FUN_0002c8fe) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0002c8fe(void)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  ushort uVar5;
  byte bVar6;
  byte bVar7;
  ushort uVar8;
  int unaff_gp;
  undefined1 uVar9;
  char cVar10;
  ushort uVar11;
  ushort uVar12;
  ushort uVar13;
  ushort uVar14;
  ushort uVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  uint uVar19;
  uint uVar20;
  uint uVar21;
  
  uVar8 = _DAT_fef005d4;
  uVar14 = *(ushort *)(unaff_gp + -0x5bd6);
  uVar21 = (uint)*(ushort *)(unaff_gp + -0x5c10);
  uVar20 = (uint)_DAT_fef005d0;
  uVar19 = (uint)_DAT_fef02622;
  iVar16 = FUN_00029662();
  iVar17 = FUN_00029662();
  uVar11 = FUN_000a1fca(&PTR_DAT_001512e8,uVar21);
  uVar12 = FUN_000a1fca(&PTR_DAT_001512d4,uVar21);
  bVar7 = DAT_00154e19;
  bVar6 = DAT_00154e18;
  uVar5 = DAT_00154d0c;
  uVar4 = DAT_00154d0a;
  uVar3 = DAT_00154d08;
  uVar2 = DAT_00154d06;
  uVar1 = DAT_00154d04;
  FUN_00037122();
  FUN_00037106();
  uVar9 = FUN_0003759e();
  cVar10 = FUN_0008a1b2();
  uVar13 = FUN_000a1cc2((uint)_DAT_febf5e86 - (uint)_DAT_fef005ce,0xffff,uVar9);
  uVar14 = FUN_000a1cc2((int)((uint)uVar14 * 0xf53 + -0x7a98000) / 0x3d09 -
                        (int)(uVar20 * 0x19 + -0xc8000) / 0x80,0xffff,0);
  iVar18 = FUN_000a1b5c(*(ushort *)(unaff_gp + -0x5bd2) - 0x8000);
  uVar15 = FUN_000a1cc2(iVar18 + 0x8000,0xffff,0);
  if (((((cVar10 == '\x01') && (iVar16 == 0)) && (uVar15 <= uVar1)) &&
      ((uVar12 < uVar13 && (uVar2 < uVar14)))) && ((uVar20 < uVar4 && (uVar5 < uVar8)))) {
    iVar17 = (uint)(bVar6 <= DAT_fef00602) + iVar17 * (uint)(bVar6 > DAT_fef00602);
    DAT_fef00602 = FUN_000a1cd2(DAT_fef00602,1);
  }
  else {
    DAT_fef00602 = 0;
  }
  uVar14 = FUN_000a1cc2(uVar21 - uVar19,0xffff,0);
  if ((iVar16 == 1) && ((uVar14 < uVar11 || (uVar3 < uVar20)))) {
    iVar17 = iVar17 * (uint)(DAT_fef00603 < bVar7);
    DAT_fef00603 = FUN_000a1cd2(DAT_fef00603,1);
  }
  else {
    DAT_fef00603 = 0;
  }
  FUN_0002966c(iVar17);
  return;
}

