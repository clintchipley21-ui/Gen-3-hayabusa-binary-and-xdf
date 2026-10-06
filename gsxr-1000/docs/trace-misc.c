
// ===== FUNCTION 0x4a8d4 (FUN_0004a8b6) =====

int FUN_0004a8b6(byte param_1)

{
  int unaff_gp;
  undefined **ppuVar1;
  int iVar2;
  
  if (param_1 < 2) {
    if (param_1 == 0) {
      ppuVar1 = &PTR_DAT_00156708;
    }
    else {
      ppuVar1 = (undefined **)&DAT_0015671c;
    }
    iVar2 = FUN_000a1fca(ppuVar1,*(undefined2 *)(unaff_gp + -0x5c86));
    iVar2 = iVar2 >> 8;
  }
  else {
    iVar2 = 0;
  }
  return iVar2;
}


// ===== FUNCTION 0x4aa16 (FUN_0004a9f8) =====

int FUN_0004a9f8(byte param_1)

{
  int unaff_gp;
  undefined *puVar1;
  int iVar2;
  
  if (param_1 < 2) {
    if (param_1 == 0) {
      puVar1 = &DAT_00156730;
    }
    else {
      puVar1 = &DAT_00156744;
    }
    iVar2 = FUN_000a1fca(puVar1,*(undefined2 *)(unaff_gp + -0x5c86));
    iVar2 = iVar2 >> 8;
  }
  else {
    iVar2 = 0;
  }
  return iVar2;
}


// ===== FUNCTION 0x59a9e (FUN_000599d8) =====

/* WARNING: Heritage AFTER dead removal. Example location: r7 : 0x00059a7e */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Restarted to delay deadcode elimination for space: register */

void FUN_000599d8(undefined4 param_1,undefined4 param_2)

{
  byte bVar1;
  byte bVar2;
  int unaff_gp;
  byte bVar3;
  short sVar4;
  ushort uVar5;
  ushort uVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  byte bVar10;
  uint uVar11;
  
  bVar2 = DAT_00171115;
  bVar1 = DAT_00171114;
  bVar10 = *(byte *)(unaff_gp + -0x5b67);
  iVar7 = FUN_00083184();
  uVar6 = _DAT_fef0119e;
  uVar5 = _DAT_fef0119c;
  uVar8 = (uint)_DAT_fef01204;
  uVar9 = (uint)_DAT_fef01202;
  uVar11 = (uint)DAT_fef01214;
  sVar4 = (ushort)DAT_fef072c6 << 5;
  bVar3 = DAT_fef011a0;
  if ((DAT_fef072c1 & 0x10) != 0) goto LAB_00059ad8;
  if (iVar7 == 1) {
LAB_00059a4c:
    uVar5 = FUN_000a1fca(&DAT_0017075c);
    uVar11 = 0x80;
    uVar6 = 0;
    bVar3 = 0xff;
  }
  else {
    if ((bVar10 & 1) == 1) goto LAB_00059a4c;
    if (_DAT_fef0119c <= _DAT_fef0119e) {
      bVar10 = DAT_fef011a0;
      if (bVar1 <= DAT_fef011a0) {
        uVar11 = FUN_000a1cac(uVar11 - bVar2,param_2,DAT_fef072c1 & 0x10);
        uVar11 = uVar11 & 0xff;
        bVar10 = 0;
      }
      bVar3 = FUN_000a1cd2(bVar10);
    }
    uVar6 = FUN_000a1cf6(uVar6);
  }
  uVar9 = FUN_000a1fca(&DAT_0017079c);
  uVar8 = FUN_000a1fca(&DAT_001707dc);
  sVar4 = FUN_000a1cc2((int)(uVar11 * uVar9 + uVar8 * (0x80 - uVar11)) / 0x80,param_2,0);
LAB_00059ad8:
  _DAT_fef01202 = (short)uVar9;
  _DAT_fef0119c = uVar5;
  DAT_fef011a0 = bVar3;
  _DAT_fef0119e = uVar6;
  DAT_fef01214 = (char)uVar11;
  _DAT_fef01204 = (short)uVar8;
  _DAT_fef01200 = sVar4;
  return;
}


// ===== FUNCTION 0x5a300 (FUN_0005a2ea) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0005a2ea(ushort param_1)

{
  undefined2 uVar1;
  
  uVar1 = 0;
  if (param_1 < DAT_001710e2) {
    uVar1 = FUN_000a1fca(&PTR_DAT_00170390,param_1);
  }
  _DAT_fef01208 = uVar1;
  return;
}


// ===== FUNCTION 0x5ad76 (FUN_0005ad08) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0005ad08(void)

{
  byte bVar1;
  ushort uVar2;
  byte bVar3;
  char cVar4;
  int unaff_gp;
  undefined **ppuVar5;
  ushort uVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  int iVar11;
  uint uVar12;
  
  cVar4 = DAT_001710fc;
  uVar2 = *(ushort *)(unaff_gp + -0x5c80);
  iVar9 = DAT_001710ac - 0x8000;
  uVar10 = (uint)_DAT_fef01200;
  uVar7 = (uint)_DAT_fef01210;
  uVar12 = (uint)_DAT_fef0120e;
  iVar8 = DAT_001710ae - 0x8000;
  if (DAT_fef011db < DAT_001710fb) {
    return;
  }
  iVar11 = uVar2 - uVar10;
  _DAT_fef011ca = FUN_000a1b5c(iVar11);
  bVar3 = (byte)((uint)iVar11 >> 0x18);
  bVar1 = (byte)((uint)iVar9 >> 0x1f);
  if (iVar11 - iVar9 < 0 == (bVar3 >> 7 != bVar1 && bVar1 == (byte)((uint)(iVar11 - iVar9) >> 0x1f))
     ) {
    uVar6 = 0;
    bVar1 = (byte)((uint)iVar8 >> 0x1f);
    if (iVar11 - iVar8 < 0 !=
        (bVar3 >> 7 != bVar1 && bVar1 == (byte)((uint)(iVar11 - iVar8) >> 0x1f)) || iVar11 == iVar8)
    goto LAB_0005ad8e;
    ppuVar5 = &PTR_DAT_00170544;
  }
  else {
    ppuVar5 = &PTR_DAT_00170530;
  }
  uVar6 = FUN_000a1fca(ppuVar5);
LAB_0005ad8e:
  _DAT_fef011cc = uVar6;
  if (cVar4 == '\0') {
    uVar12 = FUN_000a1c02(uVar7 + uVar12);
    uVar12 = uVar12 & 0xffff;
  }
  if (uVar2 < uVar10) {
    _DAT_fef0120e = FUN_000a1c02(_DAT_fef011cc + uVar12,0xffff);
  }
  else {
    _DAT_fef0120e = FUN_000a1ba0(uVar12 - _DAT_fef011cc,0);
  }
  DAT_fef011db = 0;
  FUN_0005a720(cVar4 == '\0');
  return;
}


// ===== FUNCTION 0x5af8c (FUN_0005af24) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0005af24(void)

{
  bool bVar1;
  char cVar2;
  int unaff_gp;
  undefined *puVar3;
  
  cVar2 = *(char *)(unaff_gp + -0x5bbe);
  if (cVar2 == '\x02') {
    if (DAT_0017110e == '\x03') goto LAB_0005afa8;
    if (DAT_0017110e != '\x02') goto LAB_0005af8c;
  }
  else {
    if (cVar2 == '\x04') {
      if (DAT_0017110f == '\x03') goto LAB_0005afa8;
      bVar1 = DAT_0017110f == '\x02';
    }
    else if (cVar2 == '\b') {
      if (DAT_00171110 == '\x03') goto LAB_0005afa8;
      bVar1 = DAT_00171110 == '\x02';
    }
    else if (cVar2 == '\x10') {
      if (DAT_00171111 == '\x03') goto LAB_0005afa8;
      bVar1 = DAT_00171111 == '\x02';
    }
    else if (cVar2 == ' ') {
      if (DAT_00171112 == '\x03') {
LAB_0005afa8:
        puVar3 = &LAB_00170aac;
        goto LAB_0005afc2;
      }
      bVar1 = DAT_00171112 == '\x02';
    }
    else {
      if (DAT_00171113 == '\x03') goto LAB_0005afa8;
      bVar1 = DAT_00171113 == '\x02';
    }
    if (!bVar1) {
LAB_0005af8c:
      puVar3 = &DAT_00170a1c;
      goto LAB_0005afc2;
    }
  }
  puVar3 = &DAT_00170a64;
LAB_0005afc2:
  _DAT_fef011de =
       FUN_000a201e(puVar3,*(undefined2 *)(unaff_gp + -0x5c86),*(undefined1 *)(unaff_gp + -0x5bc0));
  return;
}


// ===== FUNCTION 0x5b4ea (FUN_0005b4cc) =====

/* WARNING: Heritage AFTER dead removal. Example location: r7 : 0x0005b52e */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Restarted to delay deadcode elimination for space: register */

void FUN_0005b4cc(undefined4 param_1,undefined4 param_2)

{
  int unaff_gp;
  int iVar1;
  uint uVar2;
  
  if ((*(byte *)(unaff_gp + -0x5b67) & 1) == 0) {
    uVar2 = (uint)DAT_fef01214;
    _DAT_fef011f0 = FUN_000a1fca(&PTR_DAT_0017040c);
    iVar1 = FUN_000a1fca(&PTR_DAT_00170420);
    _DAT_fef011f2 = (undefined2)iVar1;
    _DAT_fef011ee =
         FUN_000a1cc2((int)(uVar2 * _DAT_fef011f0 + iVar1 * (0x80 - uVar2)) / 0x80,param_2,0);
  }
  else {
    _DAT_fef011ee = 0;
  }
  return;
}


// ===== FUNCTION 0x77fb0 (FUN_00077f88) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00077f88(void)

{
  char cVar1;
  int unaff_gp;
  undefined **ppuVar2;
  int iVar3;
  
  iVar3 = FUN_0003759e();
  cVar1 = *(char *)(unaff_gp + -0x5b80);
  if (iVar3 == 1) {
LAB_00077fc4:
    _DAT_fef02220 = 0;
  }
  else {
    if (cVar1 == '\x01') {
      ppuVar2 = &PTR_DAT_001716e8;
    }
    else if (cVar1 == '\x02') {
      ppuVar2 = &PTR_DAT_001716fc;
    }
    else {
      if (cVar1 != '\x03') goto LAB_00077fc4;
      ppuVar2 = &PTR_DAT_00171710;
    }
    _DAT_fef02220 = FUN_000a1fca(ppuVar2,*(undefined2 *)(unaff_gp + -0x5bd6));
  }
  return;
}


// ===== FUNCTION 0x7803a (FUN_00078006) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00078006(void)

{
  char cVar1;
  int unaff_gp;
  undefined *puVar2;
  int iVar3;
  
  iVar3 = FUN_0003759e();
  cVar1 = *(char *)(unaff_gp + -0x5b80);
  if (cVar1 == '\x01') {
    puVar2 = &DAT_001716ac;
  }
  else {
    if (cVar1 != '\x02') {
      if (cVar1 != '\x03') {
        return;
      }
      if (iVar3 != 1) {
        if (iVar3 != 0) {
          return;
        }
        puVar2 = &DAT_001716d4;
        goto LAB_0007804c;
      }
    }
    puVar2 = &DAT_001716c0;
  }
LAB_0007804c:
  _DAT_fef02222 = FUN_000a1fca(puVar2,*(undefined2 *)(unaff_gp + -0x5c0c));
  return;
}


// ===== FUNCTION 0x78990 (FUN_00078942) =====

int FUN_00078942(char param_1)

{
  int unaff_gp;
  int iVar1;
  
  if (param_1 == '\x01') {
    iVar1 = 0;
  }
  else if (param_1 == '\x02') {
    iVar1 = 1;
  }
  else if (param_1 == '\x04') {
    iVar1 = 2;
  }
  else if (param_1 == '\b') {
    iVar1 = 3;
  }
  else if (param_1 == '\x10') {
    iVar1 = 4;
  }
  else if (param_1 == ' ') {
    iVar1 = 5;
  }
  else {
    iVar1 = 6;
  }
  iVar1 = FUN_000a201e((&PTR_PTR_DAT_001719cc)[iVar1],*(undefined2 *)(unaff_gp + -0x5c3c),
                       *(undefined2 *)(unaff_gp + -0x5c86));
  return iVar1 >> 8;
}


// ===== FUNCTION 0x79262 (FUN_0007919a) =====

void FUN_0007919a(void)

{
  bool bVar1;
  char cVar2;
  undefined2 uVar3;
  undefined2 uVar4;
  byte bVar5;
  byte bVar6;
  int unaff_gp;
  undefined **ppuVar7;
  char cVar8;
  char cVar9;
  char extraout_var;
  uint uVar10;
  uint uVar11;
  char cVar12;
  char cStack_29;
  
  bVar6 = DAT_00172f47;
  cStack_29 = *(char *)(unaff_gp + -0x5d12);
  uVar11 = (uint)*(byte *)(unaff_gp + -0x5d19);
  cVar9 = *(char *)(unaff_gp + -0x5d1a);
  uVar3 = *(undefined2 *)(unaff_gp + -0x5c86);
  uVar4 = *(undefined2 *)(unaff_gp + -0x5c3c);
  cVar2 = *(char *)(unaff_gp + -0x5bbe);
  bVar5 = *(byte *)(unaff_gp + -0x5e75);
  uVar10 = (uint)DAT_00172f44;
  if ((int)((uint)DAT_fef072c3 << 0x19) < 0) {
    cVar8 = -((int)((uint)DAT_fef072c3 << 0x18) < 0);
  }
  else if ((DAT_00155c93 == '\0') ||
          (cVar8 = DAT_00172f43, (*(byte *)(unaff_gp + -0x5d11) & 1) == 0)) {
    if (DAT_00172f45 == -0x80) {
      bVar1 = (bVar5 & 1) == 1;
    }
    else {
      bVar1 = (int)((uint)*(byte *)(unaff_gp + -0x5e75) << 0x1c) < 0;
    }
    if (bVar1) {
      cVar12 = '\x01';
    }
    else {
      cVar12 = DAT_fef02251;
      if (DAT_fef02251 == '\x01') {
        bVar1 = (bVar5 & 1) == 0;
        cVar12 = bVar1 * '\x02' + !bVar1;
      }
    }
    uVar11 = FUN_00078942(cVar2);
    if (cVar12 == '\x01' || cVar12 == '\x02') {
      if (cVar2 == '\b') {
        ppuVar7 = &PTR_DAT_00171870;
      }
      else if (cVar2 == '\x10') {
        ppuVar7 = &PTR_DAT_00171898;
      }
      else {
        ppuVar7 = &PTR_DAT_00171848;
      }
      FUN_000a201e(ppuVar7,uVar4,uVar3);
      *(char *)(unaff_gp + -0x5d1c) = extraout_var;
      if (cVar12 == '\x01') {
        DAT_fef02252 = 0;
        cVar8 = extraout_var;
      }
      else {
        cVar9 = FUN_00079124(uVar11);
        cVar8 = cVar9;
        if ((*(byte *)(unaff_gp + -0x5d1c) < uVar11) &&
           (DAT_fef02251 = cVar12, *(byte *)(unaff_gp + -0x5d1b) < bVar6)) goto LAB_000792c4;
        cVar12 = '\0';
        cVar9 = '\0';
      }
      *(undefined1 *)(unaff_gp + -0x5d1b) = 0;
      DAT_fef02251 = cVar12;
    }
    else {
      FUN_000a1a94(&cStack_29,(-uVar10 & 0xff) << 8,uVar11);
      cVar8 = cStack_29;
      DAT_fef02251 = cVar12;
    }
  }
LAB_000792c4:
  *(char *)(unaff_gp + -0x5d1a) = cVar9;
  *(char *)(unaff_gp + -0x5d19) = (char)uVar11;
  *(char *)(unaff_gp + -0x5d35) = cVar8;
  *(char *)(unaff_gp + -0x5d12) = cStack_29;
  return;
}

