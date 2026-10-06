
// ===== FUNCTION 0x2b76c (FUN_0002b720) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0002b720(void)

{
  int unaff_gp;
  
  if (DAT_00154dd2 == '\0') {
    FUN_0002a11c();
    FUN_0002a16a();
    FUN_0002a19a();
    FUN_0002a220();
    FUN_0002a8f4();
    FUN_0002af60();
    FUN_0002b160();
    FUN_0002b180();
    FUN_0002b1cc();
    FUN_0002b272();
    FUN_0002b2a0();
    FUN_0002b63a();
    FUN_0002b666();
    FUN_00029f34();
    FUN_0002b6f8();
  }
  else {
    FUN_00029e0a(0);
    FUN_00029e26(0);
    DAT_fef005f6 = 0;
    DAT_fef005f7 = 0;
    FUN_00029e42(0);
    FUN_00029e5e(0);
    FUN_00029e7a(0);
    FUN_00029e96(0);
    FUN_00029eb2(0);
    *(undefined2 *)(unaff_gp + -0x618a) = 0x100;
    DAT_febf5e8d = 0x40;
    FUN_00029ece(0);
    FUN_00029eea(0);
    FUN_0002a220();
    FUN_00029f06(0);
    FUN_00029f22(0);
    _DAT_fef005f2 = 0xffff;
  }
  return;
}


// ===== FUNCTION 0x2b7b0 (FUN_0002b720) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0002b720(void)

{
  int unaff_gp;
  
  if (DAT_00154dd2 == '\0') {
    FUN_0002a11c();
    FUN_0002a16a();
    FUN_0002a19a();
    FUN_0002a220();
    FUN_0002a8f4();
    FUN_0002af60();
    FUN_0002b160();
    FUN_0002b180();
    FUN_0002b1cc();
    FUN_0002b272();
    FUN_0002b2a0();
    FUN_0002b63a();
    FUN_0002b666();
    FUN_00029f34();
    FUN_0002b6f8();
  }
  else {
    FUN_00029e0a(0);
    FUN_00029e26(0);
    DAT_fef005f6 = 0;
    DAT_fef005f7 = 0;
    FUN_00029e42(0);
    FUN_00029e5e(0);
    FUN_00029e7a(0);
    FUN_00029e96(0);
    FUN_00029eb2(0);
    *(undefined2 *)(unaff_gp + -0x618a) = 0x100;
    DAT_febf5e8d = 0x40;
    FUN_00029ece(0);
    FUN_00029eea(0);
    FUN_0002a220();
    FUN_00029f06(0);
    FUN_00029f22(0);
    _DAT_fef005f2 = 0xffff;
  }
  return;
}


// ===== FUNCTION 0x2a6e8 (FUN_0002a698) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0002a698(void)

{
  ushort uVar1;
  undefined2 uVar2;
  ushort uVar3;
  ushort uVar4;
  int unaff_gp;
  int iVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  
  uVar4 = _DAT_fef00570;
  uVar3 = _DAT_fef0056e;
  uVar1 = *(ushort *)(unaff_gp + -0x5c60);
  uVar2 = *(undefined2 *)(unaff_gp + -0x5c86);
  uVar8 = (uint)_DAT_fef00592;
  uVar7 = (uint)DAT_fef005b1;
  iVar5 = FUN_00029efc();
  uVar9 = (uint)DAT_fef005f6;
  uVar6 = FUN_000a1fca(&PTR_DAT_00150a58,uVar2);
  if (iVar5 != 1) {
    iVar5 = 0;
    _DAT_fef00592 = 0;
    goto LAB_0002a71e;
  }
  iVar5 = (uint)(4 < uVar9) + uVar9 * (uVar9 < 5);
  if ((int)(uVar7 << 0x1e) < 0) {
    if (iVar5 == 1) goto LAB_0002a6ee;
LAB_0002a6f6:
    if (iVar5 == 2) goto LAB_0002a6fa;
LAB_0002a702:
    if (iVar5 != 3) {
      _DAT_fef00592 = 0;
      goto LAB_0002a71e;
    }
  }
  else {
    iVar5 = 1;
LAB_0002a6ee:
    if (uVar1 <= uVar3) goto LAB_0002a6f6;
    iVar5 = 2;
LAB_0002a6fa:
    if (uVar1 <= uVar4) goto LAB_0002a702;
    iVar5 = 3;
  }
  iVar5 = (uint)(uVar6 <= uVar8) * 4 + iVar5 * (uint)(uVar6 > uVar8);
  _DAT_fef00592 = FUN_000a1cf6(uVar8,1);
LAB_0002a71e:
  DAT_fef005f6 = (char)iVar5;
  return;
}


// ===== FUNCTION 0x2a696 (FUN_0002a652) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0002a652(void)

{
  undefined2 uVar1;
  byte bVar2;
  int unaff_gp;
  undefined2 uVar3;
  int iVar4;
  undefined4 uVar5;
  
  bVar2 = DAT_fef005b1;
  uVar3 = _DAT_fef00570;
  uVar1 = _DAT_febf5e78;
  iVar4 = FUN_00029efc();
  if (((bVar2 & 2) == 0) && (iVar4 == 1)) {
    uVar5 = FUN_000a1fca(&DAT_0015096c,*(undefined1 *)(unaff_gp + -0x5bbe));
    uVar3 = FUN_000a1cf6(uVar1,uVar5);
  }
  _DAT_fef00570 = uVar3;
  return;
}


// ===== FUNCTION 0x2aa62 (FUN_0002a96e) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0002a96e(void)

{
  bool bVar1;
  char cVar2;
  ushort uVar3;
  ushort uVar4;
  bool bVar5;
  ushort uVar6;
  ushort uVar7;
  char cVar8;
  ushort uVar9;
  ushort uVar10;
  ushort uVar11;
  ushort uVar12;
  ushort uVar13;
  ushort uVar14;
  ushort uVar15;
  ushort uVar16;
  int unaff_gp;
  char cVar17;
  char cVar18;
  ushort uVar19;
  ushort uVar20;
  undefined2 uVar21;
  int iVar22;
  uint uVar23;
  uint uVar24;
  int iVar25;
  uint uVar26;
  byte bVar27;
  char cVar28;
  
  uVar16 = _DAT_fef00588;
  uVar15 = _DAT_fef00580;
  uVar14 = _DAT_fef00578;
  uVar13 = _DAT_fef00572;
  uVar12 = _DAT_fef0056c;
  uVar11 = _DAT_fef0056a;
  uVar10 = DAT_001559bc;
  uVar9 = DAT_001559ba;
  cVar8 = DAT_00154dd5;
  cVar28 = DAT_00154dd4;
  uVar7 = DAT_00154c7e;
  uVar6 = DAT_00154c7c;
  uVar24 = (uint)DAT_fef005a2;
  uVar3 = *(ushort *)(unaff_gp + -0x5c60);
  bVar27 = DAT_fef005a3 & 1;
  uVar4 = *(ushort *)(unaff_gp + -0x5c86);
  uVar26 = (uint)_DAT_fef02630;
  cVar2 = *(char *)(unaff_gp + -0x5bbe);
  cVar17 = FUN_00085dbe();
  cVar18 = FUN_00029efc();
  uVar23 = (uint)DAT_fef005b1;
  iVar25 = -((int)((uint)DAT_fef005a3 << 0x1d) >> 0x1f);
  iVar22 = FUN_00029f18();
  bVar5 = false;
  bVar1 = false;
  uVar19 = FUN_000a1fca(&PTR_DAT_001509a8,cVar2);
  uVar20 = FUN_000a1fca(&DAT_001509bc,cVar2);
  if (uVar3 <= uVar13) {
    if (cVar28 == -0x80) {
      if ((((uint)uVar10 * 0x40 <= uVar26) && (uVar26 <= (uint)uVar9 * 0x40)) &&
         ((uVar26 <= uVar11 || (uVar12 <= uVar26)))) {
        bVar1 = uVar6 <= uVar15;
        uVar21 = FUN_000a1cf6(uVar15,1);
        goto LAB_0002aaa4;
      }
    }
    else if (uVar13 < uVar14) {
      bVar5 = true;
    }
  }
  uVar21 = 0;
LAB_0002aaa4:
  if (((bVar5) || (bVar1)) && ((cVar8 != -0x80 || (cVar17 == '\0')))) {
    cVar28 = '\x01';
    _DAT_fef00588 = 0;
  }
  else {
    cVar28 = bVar27 * (uVar16 < uVar7);
    _DAT_fef00588 = FUN_000a1cf6(uVar16,1);
  }
  if (cVar28 == '\x01') {
    DAT_fef005a3 = DAT_fef005a3 | 1;
    if ((int)(uVar24 << 0x1e) < 0) {
      if ((((uVar19 < uVar4) && (uVar4 < uVar20)) && (cVar2 != '\x01')) && (cVar2 != '\x02')) {
        iVar22 = 1;
      }
      else if ((-1 < (int)(uVar23 << 0x1d)) && (cVar18 == '\0')) {
        iVar25 = (uint)(iVar22 == 0) + iVar25 * (uint)(iVar22 != 0);
      }
    }
  }
  else {
    DAT_fef005a3 = DAT_fef005a3 & 0xfe;
  }
  _DAT_fef00580 = uVar21;
  FUN_00029f22(iVar22);
  if (iVar25 == 1) {
    DAT_fef005a3 = DAT_fef005a3 | 4;
  }
  else {
    DAT_fef005a3 = DAT_fef005a3 & 0xfb;
  }
  return;
}

