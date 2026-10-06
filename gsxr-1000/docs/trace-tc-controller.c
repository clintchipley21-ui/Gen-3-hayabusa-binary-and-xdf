
// ===== FUNCTION 0x55016 (FUN_00055016) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00055016(void)

{
  char cVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  ushort uVar7;
  ushort uVar8;
  ushort uVar9;
  ushort uVar10;
  ushort uVar11;
  ushort uVar12;
  ushort uVar13;
  ushort uVar14;
  ushort uVar15;
  char cVar16;
  ushort uVar17;
  int unaff_gp;
  undefined **ppuVar18;
  uint uVar19;
  undefined2 uVar20;
  int iVar21;
  int iVar22;
  int iVar23;
  int iVar24;
  int iVar25;
  undefined *puVar26;
  undefined *puVar27;
  undefined **ppuVar28;
  int iVar29;
  
  cVar16 = DAT_001702c4;
  uVar15 = DAT_00170200;
  uVar14 = DAT_001701fe;
  uVar13 = DAT_001701fc;
  uVar12 = DAT_001701fa;
  uVar11 = DAT_001701f8;
  uVar10 = DAT_001701f6;
  uVar9 = DAT_001701f4;
  uVar8 = DAT_001701f2;
  uVar7 = DAT_001701f0;
  uVar6 = DAT_001701ee;
  uVar5 = DAT_001701ec;
  uVar4 = DAT_001701e4;
  cVar1 = *(char *)(unaff_gp + -0x5ba7);
  iVar21 = FUN_00028340();
  uVar17 = _DAT_febf6164;
  uVar20 = *(undefined2 *)(unaff_gp + -0x5f0c);
  uVar2 = *(undefined2 *)(unaff_gp + -0x5c06);
  if (cVar1 == '\x01') {
    ppuVar18 = &PTR_DAT_00168550;
    ppuVar28 = (undefined **)&DAT_00168564;
    puVar27 = &DAT_00168578;
    puVar26 = &DAT_0016858c;
  }
  else if (cVar1 == '\x02') {
    ppuVar18 = &PTR_DAT_00168608;
    ppuVar28 = (undefined **)0x16861c;
    puVar27 = (undefined *)0x168630;
    puVar26 = (undefined *)0x168644;
  }
  else if (cVar1 == '\x03') {
    ppuVar18 = &PTR_DAT_001686c0;
    ppuVar28 = (undefined **)0x1686d4;
    puVar27 = (undefined *)0x1686e8;
    puVar26 = (undefined *)0x1686fc;
  }
  else if (cVar1 == '\x04') {
    ppuVar18 = &PTR_DAT_00168778;
    ppuVar28 = &PTR_DAT_0016878c;
    puVar27 = (undefined *)0x1687a0;
    puVar26 = (undefined *)0x1687b4;
  }
  else if (cVar1 == '\x05') {
    ppuVar18 = &PTR_DAT_00168830;
    ppuVar28 = (undefined **)0x168844;
    puVar27 = (undefined *)0x168858;
    puVar26 = (undefined *)0x16886c;
  }
  else if (cVar1 == '\x06') {
    ppuVar18 = &PTR_DAT_001688e8;
    ppuVar28 = &PTR_DAT_001688fc;
    puVar27 = (undefined *)0x168910;
    puVar26 = (undefined *)0x168924;
  }
  else if (cVar1 == '\a') {
    ppuVar18 = &PTR_DAT_001689a0;
    ppuVar28 = (undefined **)0x1689b4;
    puVar27 = (undefined *)0x1689c8;
    puVar26 = (undefined *)0x1689dc;
  }
  else if (cVar1 == '\b') {
    ppuVar18 = &PTR_DAT_00168a58;
    ppuVar28 = (undefined **)0x168a6c;
    puVar27 = (undefined *)0x168a80;
    puVar26 = (undefined *)0x168a94;
  }
  else if (cVar1 == '\t') {
    ppuVar18 = &PTR_DAT_00168b10;
    ppuVar28 = &PTR_DAT_00168b24;
    puVar27 = (undefined *)0x168b38;
    puVar26 = (undefined *)0x168b4c;
  }
  else {
    ppuVar18 = &PTR_DAT_00168bc8;
    ppuVar28 = &PTR_DAT_00168bdc;
    puVar27 = (undefined *)0x168bf0;
    puVar26 = (undefined *)0x168c04;
  }
  iVar22 = FUN_000a1fca(ppuVar18,_DAT_febf6164);
  *(short *)(unaff_gp + -0x5f00) = (short)iVar22;
  if (cVar16 == -0x80) {
    uVar20 = FUN_000a1cc2((uint)*(ushort *)(unaff_gp + -0x5f02) + iVar22 + -0x8000,0xffff,0);
  }
  else {
    uVar3 = *(undefined2 *)(unaff_gp + -0x5bd0);
    iVar23 = FUN_000a1fca(ppuVar28,uVar20);
    iVar24 = FUN_000a1fca(puVar27,uVar2);
    iVar25 = FUN_000a1fca(puVar26,uVar3);
    if ((((*(byte *)(unaff_gp + -0x5ed6) & 0x80) != 0) && ((*(byte *)(unaff_gp + -0x5ed5) & 1) != 0)
        ) || ((((*(byte *)(unaff_gp + -0x5ed6) & 0x80) == 0 ||
               (iVar29 = iVar23, (*(byte *)(unaff_gp + -0x5ed5) & 1) != 0)) &&
              (((*(byte *)(unaff_gp + -0x5ed6) & 0x80) != 0 ||
               (iVar29 = iVar24, (*(byte *)(unaff_gp + -0x5ed5) & 1) == 0)))))) {
      iVar29 = 0x8000;
    }
    if (uVar4 < uVar17) {
      iVar25 = 100;
    }
    uVar20 = FUN_000a1cc2(iVar29 + (uint)(iVar22 * iVar25) / 100 + -0x8000,0xffff,0);
    *(short *)(unaff_gp + -0x5f04) = (short)iVar29;
    *(short *)(unaff_gp + -0x5f0a) = (short)iVar23;
    *(short *)(unaff_gp + -0x5f08) = (short)iVar24;
    *(short *)(unaff_gp + -0x5f06) = (short)iVar25;
  }
  if ((*(byte *)(unaff_gp + -0x5ed5) & 8) != 0) {
    if (iVar21 == 0) {
      if (cVar1 == '\x01') {
        uVar19 = (uint)uVar5;
      }
      else if (cVar1 == '\x02') {
        uVar19 = (uint)uVar6;
      }
      else if (cVar1 == '\x03') {
        uVar19 = (uint)uVar7;
      }
      else if (cVar1 == '\x04') {
        uVar19 = (uint)uVar8;
      }
      else if (cVar1 == '\x05') {
        uVar19 = (uint)uVar9;
      }
      else if (cVar1 == '\x06') {
        uVar19 = (uint)uVar10;
      }
      else if (cVar1 == '\a') {
        uVar19 = (uint)uVar11;
      }
      else if (cVar1 == '\b') {
        uVar19 = (uint)uVar12;
      }
      else {
        uVar19 = (uint)uVar14 * (uint)(cVar1 != '\t') + (uint)uVar13 * (uint)(cVar1 == '\t');
      }
    }
    else {
      uVar19 = (uint)uVar15;
    }
    uVar20 = FUN_000a1bf6(uVar20,uVar19);
  }
  _DAT_febf6162 = uVar20;
  return;
}

