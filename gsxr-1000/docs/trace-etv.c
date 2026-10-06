
// ===== FUNCTION 0x2f082 (FUN_0002f028) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0002f028(void)

{
  ushort uVar1;
  ushort uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar1 = _DAT_fef02d7a;
  uVar4 = (uint)_DAT_fef005e6;
  uVar3 = (uint)_DAT_febf5e86;
  uVar2 = FUN_000a1c02();
  if (uVar2 < uVar1) {
    _DAT_fef00660 = 0x8000;
  }
  else {
    _DAT_fef00670 = FUN_000a1cc2((uVar4 - uVar3) + 0x8000,0xffff,0);
    _DAT_fef00660 = FUN_000a1fca(&PTR_DAT_0015134c);
  }
  return;
}


// ===== FUNCTION 0x2f0c8 (FUN_0002f094) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0002f094(void)

{
  _DAT_fef00674 = FUN_000a1cc2(((uint)_DAT_fef005e8 - (uint)_DAT_febf5e86) + 0x8000,0xffff,0);
  _DAT_fef00662 = FUN_000a1fca(&PTR_DAT_00151374);
  return;
}


// ===== FUNCTION 0x2f11e (FUN_0002f0da) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0002f0da(void)

{
  ushort uVar1;
  undefined2 uVar2;
  undefined4 uVar3;
  
  uVar2 = DAT_00154d9a;
  uVar1 = DAT_00154d98;
  _DAT_fef00672 = FUN_000a1cc2(((uint)_DAT_fef005e2 - (uint)_DAT_febf5e86) + 0x8000,0xffff,0);
  uVar3 = FUN_000a1fca(&PTR_DAT_00151360);
  _DAT_fef00666 = (undefined2)uVar3;
  if ((DAT_fef005f8 == '\r') && (_DAT_fef0068c < uVar1)) {
    uVar3 = FUN_000a1bf6(uVar3,uVar2);
  }
  uVar2 = 0;
  if (DAT_fef005f8 == '\r') {
    uVar2 = FUN_000a1cf6(_DAT_fef0068c,1);
  }
  _DAT_fef0068c = uVar2;
  _DAT_fef00664 = (short)uVar3;
  return;
}


// ===== FUNCTION 0x2f1b2 (FUN_0002f16a) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0002f16a(void)

{
  undefined2 uVar1;
  ushort uVar2;
  undefined2 uVar3;
  
  uVar3 = _DAT_fef00668;
  uVar2 = DAT_00154dae;
  uVar1 = DAT_00154dac;
  _DAT_fef00676 = FUN_000a1cc2(((uint)_DAT_fef005e0 - (uint)_DAT_febf5e86) + 0x8000,0xffff,0);
  _DAT_fef0066a = FUN_000a1fca(&PTR_DAT_00151388);
  if (DAT_fef005f8 == '\x0e') {
    uVar3 = _DAT_fef0066a;
    if (_DAT_fef0068e < uVar2) {
      _DAT_fef0068e = FUN_000a1cf6(_DAT_fef0068e,1);
      uVar3 = FUN_000a1bf6(_DAT_fef0066a,uVar1);
    }
  }
  else {
    _DAT_fef0068e = 0;
  }
  _DAT_fef00668 = uVar3;
  return;
}


// ===== FUNCTION 0x2f274 (FUN_0002f218) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0002f218(void)

{
  uint uVar1;
  
  uVar1 = (uint)_DAT_fef005da;
  _DAT_fef005ee = FUN_000a1c02(((uint)_DAT_fef005dc * 1000) / (uint)_DAT_fef005f0 + 0x8000,0xffff);
  _DAT_fef00678 = FUN_000a1cc2(_DAT_fef005ee - uVar1,0xffff,0);
  _DAT_fef0066c = FUN_000a1fca(&PTR_DAT_0015139c);
  return;
}


// ===== FUNCTION 0x8ae68 (FUN_0008ae3e) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0008ae3e(void)

{
  undefined2 uVar1;
  undefined2 uVar2;
  int unaff_gp;
  undefined *puVar3;
  int iVar4;
  uint uVar5;
  
  uVar2 = DAT_00192cec;
  uVar1 = DAT_00192cea;
  uVar5 = (uint)_DAT_fef02d86;
  puVar3 = &DAT_00174724;
  if (0x7fff < uVar5) {
    puVar3 = &DAT_00174710;
  }
  iVar4 = FUN_000a1fca(puVar3,*(undefined2 *)(unaff_gp + -0x5c84));
  DAT_fef02dba = (undefined1)((uint)iVar4 >> 8);
  _DAT_fef02d98 = FUN_000a1cc2((int)((uVar5 - 0x8000) * (iVar4 >> 8)) / 8 + 0x8000,uVar2,uVar1);
  return;
}


// ===== FUNCTION 0x8e45c (FUN_0008e3b8) =====

void FUN_0008e3b8(void)

{
  undefined2 uVar1;
  int unaff_gp;
  undefined **ppuVar2;
  undefined2 uVar3;
  undefined2 uVar4;
  int iVar5;
  int iVar6;
  
  uVar4 = *(undefined2 *)(unaff_gp + -0x5bca);
  uVar1 = *(undefined2 *)(unaff_gp + -0x5c82);
  iVar5 = FUN_0008c9f4();
  iVar6 = FUN_00083ae4();
  *(undefined2 *)(unaff_gp + -0x5a58) = *(undefined2 *)(unaff_gp + -0x5a5c);
  *(undefined2 *)(unaff_gp + -0x5a5c) = *(undefined2 *)(unaff_gp + -0x5a60);
  *(undefined2 *)(unaff_gp + -0x5a60) = *(undefined2 *)(unaff_gp + -0x5a64);
  *(undefined2 *)(unaff_gp + -0x5a64) = *(undefined2 *)(unaff_gp + -0x5a68);
  *(undefined2 *)(unaff_gp + -0x5a56) = *(undefined2 *)(unaff_gp + -0x5a5a);
  *(undefined2 *)(unaff_gp + -0x5a5a) = *(undefined2 *)(unaff_gp + -0x5a5e);
  *(undefined2 *)(unaff_gp + -0x5a5e) = *(undefined2 *)(unaff_gp + -0x5a62);
  *(undefined2 *)(unaff_gp + -0x5a62) = *(undefined2 *)(unaff_gp + -0x5a66);
  if (iVar5 == 0) {
    if (iVar6 == 1) {
      uVar3 = FUN_000a201e(&PTR_DAT_00193d94,uVar4,uVar1);
      ppuVar2 = &PTR_DAT_00193e54;
      goto LAB_0008e478;
    }
    if (iVar6 == 0) {
      uVar3 = FUN_000a201e(&PTR_DAT_00193df4,uVar4,uVar1);
      ppuVar2 = &PTR_DAT_00193eb4;
      goto LAB_0008e478;
    }
  }
  if ((iVar5 == 1) && (iVar6 == 1)) {
    uVar3 = FUN_000a201e(&PTR_DAT_00193dc4,uVar4,uVar1);
    ppuVar2 = &PTR_DAT_00193e84;
  }
  else {
    uVar3 = FUN_000a201e(&PTR_DAT_00193e24,uVar4,uVar1);
    ppuVar2 = &PTR_DAT_00193ee4;
  }
LAB_0008e478:
  uVar4 = FUN_000a201e(ppuVar2,uVar4,uVar1);
  *(undefined2 *)(unaff_gp + -0x5a68) = uVar3;
  *(undefined2 *)(unaff_gp + -0x5a66) = uVar4;
  return;
}


// ===== FUNCTION 0x8e7d0 (FUN_0008e7ac) =====

void FUN_0008e7ac(void)

{
  int unaff_gp;
  undefined **ppuVar1;
  undefined2 uVar2;
  
  if (DAT_0019eb7e <= *(ushort *)(unaff_gp + -0x5c82)) {
    if (DAT_0019eb7c < *(ushort *)(unaff_gp + -0x5854)) {
      ppuVar1 = &PTR_DAT_00192d8c;
    }
    else {
      ppuVar1 = &PTR_DAT_00192d78;
    }
    uVar2 = FUN_000a1fca(ppuVar1);
    *(undefined2 *)(unaff_gp + -0x57de) = uVar2;
  }
  return;
}


// ===== FUNCTION 0x8c042 (FUN_0008bf80) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0008bf80(void)

{
  undefined1 uVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  undefined2 uVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  undefined2 uVar9;
  uint uVar10;
  undefined1 *puVar11;
  
  cVar7 = DAT_fef02e55;
  cVar6 = DAT_fef02e54;
  uVar9 = _DAT_fef02e32;
  uVar5 = _DAT_fef02e2c;
  cVar4 = DAT_fef0267c;
  cVar3 = DAT_fef005f7;
  cVar2 = DAT_fef005f6;
  uVar1 = DAT_febf6169;
  cVar8 = FUN_00029e8c();
  uVar10 = (uint)DAT_fef02e56;
  if ((cVar2 == '\x01') && (cVar6 == '\0')) {
    uVar9 = FUN_000a201e(&LAB_00174d18,uVar5,uVar1);
    _DAT_fef02e04 = &LAB_00174d18;
  }
  if ((((cVar2 == '\x02') && (cVar6 == '\x01')) || ((cVar2 == '\x03' && (cVar6 == '\x02')))) ||
     ((cVar2 == '\x04' && (cVar6 == '\x03')))) {
    uVar9 = FUN_000a201e(&LAB_00174d64,uVar5,uVar1);
    _DAT_fef02e04 = &LAB_00174d64;
  }
  if ((cVar3 == '\x01') && (cVar7 == '\0')) {
    if (cVar4 == '\x01') {
      puVar11 = &DAT_00174dfc;
    }
    else if (cVar4 == '\x02') {
      puVar11 = &LAB_00174e48;
    }
    else {
      puVar11 = &DAT_00174db0;
    }
    uVar9 = FUN_000a201e(puVar11,uVar5,uVar1);
    _DAT_fef02e04 = puVar11;
    _DAT_fef02e2e = uVar9;
  }
  if ((((cVar3 == '\x02') && (cVar7 == '\x01')) || ((cVar3 == '\x03' && (cVar7 == '\x02')))) ||
     ((cVar3 == '\x04' && (cVar7 == '\x03')))) {
    if (cVar4 == '\x01') {
      puVar11 = &LAB_00174ee0;
    }
    else if (cVar4 == '\x02') {
      puVar11 = &LAB_00174f2c;
    }
    else {
      puVar11 = &LAB_00174e94;
    }
    uVar9 = FUN_000a201e(puVar11,uVar5,uVar1);
    _DAT_fef02e04 = puVar11;
    _DAT_fef02e30 = uVar9;
  }
  if ((cVar8 == '\x01') && (-1 < (int)(uVar10 << 0x1e))) {
    uVar9 = FUN_000a201e(&DAT_00174f78,uVar5,uVar1);
    _DAT_fef02e04 = &DAT_00174f78;
  }
  DAT_fef02e54 = cVar2;
  DAT_fef02e55 = cVar3;
  if (cVar8 == '\x01') {
    DAT_fef02e56 = DAT_fef02e56 | 2;
  }
  else {
    DAT_fef02e56 = DAT_fef02e56 & 0xfd;
  }
  _DAT_fef02e32 = uVar9;
  return;
}

