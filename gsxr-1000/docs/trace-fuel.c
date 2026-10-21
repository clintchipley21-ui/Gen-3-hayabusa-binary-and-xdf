
// ===== FUNCTION 0x52880 (FUN_00052866) =====

void FUN_00052866(void)

{
  int unaff_gp;
  undefined **ppuVar1;
  undefined1 extraout_var;
  
  if (*(byte *)(unaff_gp + -0x5f64) < 0x80) {
    ppuVar1 = &PTR_DAT_00156588;
  }
  else {
    ppuVar1 = &PTR_DAT_00156574;
  }
  FUN_000a1fca(ppuVar1,*(undefined1 *)(unaff_gp + -0x5bc0));
  *(undefined1 *)(unaff_gp + -0x5f63) = extraout_var;
  return;
}


// ===== FUNCTION 0x52778 (FUN_0005275a) =====

void FUN_0005275a(undefined2 param_1)

{
  int unaff_gp;
  undefined *puVar1;
  undefined1 extraout_var;
  
  if (*(byte *)(unaff_gp + -0x5f62) < 0x80) {
    puVar1 = &DAT_00156ac0;
  }
  else {
    puVar1 = &DAT_00156a98;
  }
  FUN_000a201e(puVar1,*(undefined2 *)(unaff_gp + -0x5c3c),param_1);
  *(undefined1 *)(unaff_gp + -0x5f5e) = extraout_var;
  return;
}


// ===== FUNCTION 0x5279e (FUN_0005278c) =====

void FUN_0005278c(undefined2 param_1)

{
  int unaff_gp;
  undefined **ppuVar1;
  undefined1 extraout_var;
  
  if (*(byte *)(unaff_gp + -0x5f5f) < 0x80) {
    ppuVar1 = &PTR_DAT_001565b0;
  }
  else {
    ppuVar1 = &PTR_DAT_0015659c;
  }
  FUN_000a1fca(ppuVar1,param_1);
  *(undefined1 *)(unaff_gp + -0x5f5d) = extraout_var;
  return;
}


// ===== FUNCTION 0x527a6 (FUN_0005278c) =====

void FUN_0005278c(undefined2 param_1)

{
  int unaff_gp;
  undefined **ppuVar1;
  undefined1 extraout_var;
  
  if (*(byte *)(unaff_gp + -0x5f5f) < 0x80) {
    ppuVar1 = &PTR_DAT_001565b0;
  }
  else {
    ppuVar1 = &PTR_DAT_0015659c;
  }
  FUN_000a1fca(ppuVar1,param_1);
  *(undefined1 *)(unaff_gp + -0x5f5d) = extraout_var;
  return;
}


// ===== FUNCTION 0x526be (FUN_000526b6) =====

void FUN_000526b6(undefined2 param_1)

{
  int unaff_gp;
  undefined2 uVar1;
  
  uVar1 = FUN_000a1fca(&PTR_DAT_00156560,param_1);
  *(undefined2 *)(unaff_gp + -0x5f66) = uVar1;
  return;
}


// ===== FUNCTION 0x51912 (FUN_000518b2) =====

void FUN_000518b2(undefined1 param_1)

{
  undefined1 uVar1;
  char cVar2;
  undefined2 uVar3;
  char cVar4;
  uint uVar5;
  int unaff_gp;
  undefined *puVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  
  uVar3 = *(undefined2 *)(unaff_gp + -0x5c0a);
  uVar1 = *(undefined1 *)(unaff_gp + -0x5bbe);
  cVar2 = *(char *)(unaff_gp + -0x5ba6);
  iVar7 = FUN_0002eeac();
  uVar10 = (uint)*(byte *)(unaff_gp + -0x5f7a);
  iVar8 = FUN_00044738(0);
  iVar9 = FUN_00044738(1);
  cVar4 = DAT_0017447c;
  if ((cVar2 == '\0') || (iVar7 == 1)) {
    uVar10 = (uint)DAT_0016709c;
  }
  else {
    if (cVar2 == '\x01') {
      puVar6 = &DAT_00157588;
    }
    else if (cVar2 == '\x02') {
      puVar6 = &DAT_001575a4;
    }
    else {
      if (cVar2 != '\x03') goto LAB_00051930;
      puVar6 = &DAT_001575c0;
    }
    uVar10 = FUN_000a2344(puVar6,uVar3,uVar1);
    uVar10 = uVar10 >> 8;
  }
LAB_00051930:
  if ((iVar8 == 1) || ((cVar4 != '\0' && (iVar9 == 1)))) {
    uVar10 = 0x1e;
  }
  switch(param_1) {
  case 0:
    uVar5 = uVar10 & 2;
    break;
  case 1:
    uVar5 = uVar10 & 4;
    break;
  case 2:
    uVar5 = uVar10 & 8;
    break;
  case 3:
    uVar5 = uVar10 & 0x10;
    break;
  default:
    uVar5 = 0;
  }
  FUN_00051860(param_1,uVar5 != 0);
  *(char *)(unaff_gp + -0x5f7a) = (char)uVar10;
  return;
}


// ===== FUNCTION 0x51922 (FUN_000518b2) =====

void FUN_000518b2(undefined1 param_1)

{
  undefined1 uVar1;
  char cVar2;
  undefined2 uVar3;
  char cVar4;
  uint uVar5;
  int unaff_gp;
  undefined *puVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  
  uVar3 = *(undefined2 *)(unaff_gp + -0x5c0a);
  uVar1 = *(undefined1 *)(unaff_gp + -0x5bbe);
  cVar2 = *(char *)(unaff_gp + -0x5ba6);
  iVar7 = FUN_0002eeac();
  uVar10 = (uint)*(byte *)(unaff_gp + -0x5f7a);
  iVar8 = FUN_00044738(0);
  iVar9 = FUN_00044738(1);
  cVar4 = DAT_0017447c;
  if ((cVar2 == '\0') || (iVar7 == 1)) {
    uVar10 = (uint)DAT_0016709c;
  }
  else {
    if (cVar2 == '\x01') {
      puVar6 = &DAT_00157588;
    }
    else if (cVar2 == '\x02') {
      puVar6 = &DAT_001575a4;
    }
    else {
      if (cVar2 != '\x03') goto LAB_00051930;
      puVar6 = &DAT_001575c0;
    }
    uVar10 = FUN_000a2344(puVar6,uVar3,uVar1);
    uVar10 = uVar10 >> 8;
  }
LAB_00051930:
  if ((iVar8 == 1) || ((cVar4 != '\0' && (iVar9 == 1)))) {
    uVar10 = 0x1e;
  }
  switch(param_1) {
  case 0:
    uVar5 = uVar10 & 2;
    break;
  case 1:
    uVar5 = uVar10 & 4;
    break;
  case 2:
    uVar5 = uVar10 & 8;
    break;
  case 3:
    uVar5 = uVar10 & 0x10;
    break;
  default:
    uVar5 = 0;
  }
  FUN_00051860(param_1,uVar5 != 0);
  *(char *)(unaff_gp + -0x5f7a) = (char)uVar10;
  return;
}


// ===== FUNCTION 0x4c78c (FUN_0004c6e8) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0004c6e8(void)

{
  char cVar1;
  ushort uVar2;
  undefined2 uVar3;
  int unaff_gp;
  undefined **ppuVar4;
  undefined1 extraout_var;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  
  cVar1 = *(char *)(unaff_gp + -0x5bbe);
  uVar2 = *(ushort *)(unaff_gp + -0x5c3c);
  uVar3 = *(undefined2 *)(unaff_gp + -0x5c86);
  iVar5 = FUN_00083a80();
  iVar6 = FUN_00036b8c();
  iVar7 = FUN_00036ba8();
  iVar8 = FUN_00037122();
  iVar9 = FUN_00037106();
  if ((((DAT_fef00dcf <= DAT_00167104) && (iVar5 == 1)) && (cVar1 == '\x01')) ||
     (((iVar8 != 1 && (iVar9 != 1)) &&
      ((((uVar2 < DAT_00166ff2 ||
         ((_DAT_fef02622 < DAT_00166ff8 || (*(ushort *)(unaff_gp + -0x5c10) < DAT_00166ff8)))) ||
        (iVar6 != 0)) || (iVar7 != 0)))))) {
    DAT_febf603c = 0x80;
    return;
  }
  if (cVar1 != '\x01') {
    if (cVar1 == '\b') {
      ppuVar4 = &PTR_DAT_001575dc;
      goto LAB_0004c7b0;
    }
    if (cVar1 == '\x10') {
      ppuVar4 = (undefined **)&DAT_001575f0;
      goto LAB_0004c7b0;
    }
    if (cVar1 == ' ') {
      ppuVar4 = (undefined **)&DAT_00157604;
      goto LAB_0004c7b0;
    }
    if (cVar1 != '@') {
      DAT_febf603c = 0x80;
      return;
    }
  }
  ppuVar4 = (undefined **)&DAT_00157618;
LAB_0004c7b0:
  FUN_000a1fca(ppuVar4,uVar3);
  DAT_febf603c = extraout_var;
  return;
}


// ===== FUNCTION 0x4c796 (FUN_0004c6e8) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0004c6e8(void)

{
  char cVar1;
  ushort uVar2;
  undefined2 uVar3;
  int unaff_gp;
  undefined **ppuVar4;
  undefined1 extraout_var;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  
  cVar1 = *(char *)(unaff_gp + -0x5bbe);
  uVar2 = *(ushort *)(unaff_gp + -0x5c3c);
  uVar3 = *(undefined2 *)(unaff_gp + -0x5c86);
  iVar5 = FUN_00083a80();
  iVar6 = FUN_00036b8c();
  iVar7 = FUN_00036ba8();
  iVar8 = FUN_00037122();
  iVar9 = FUN_00037106();
  if ((((DAT_fef00dcf <= DAT_00167104) && (iVar5 == 1)) && (cVar1 == '\x01')) ||
     (((iVar8 != 1 && (iVar9 != 1)) &&
      ((((uVar2 < DAT_00166ff2 ||
         ((_DAT_fef02622 < DAT_00166ff8 || (*(ushort *)(unaff_gp + -0x5c10) < DAT_00166ff8)))) ||
        (iVar6 != 0)) || (iVar7 != 0)))))) {
    DAT_febf603c = 0x80;
    return;
  }
  if (cVar1 != '\x01') {
    if (cVar1 == '\b') {
      ppuVar4 = &PTR_DAT_001575dc;
      goto LAB_0004c7b0;
    }
    if (cVar1 == '\x10') {
      ppuVar4 = (undefined **)&DAT_001575f0;
      goto LAB_0004c7b0;
    }
    if (cVar1 == ' ') {
      ppuVar4 = (undefined **)&DAT_00157604;
      goto LAB_0004c7b0;
    }
    if (cVar1 != '@') {
      DAT_febf603c = 0x80;
      return;
    }
  }
  ppuVar4 = (undefined **)&DAT_00157618;
LAB_0004c7b0:
  FUN_000a1fca(ppuVar4,uVar3);
  DAT_febf603c = extraout_var;
  return;
}


// ===== FUNCTION 0x4c7a0 (FUN_0004c6e8) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0004c6e8(void)

{
  char cVar1;
  ushort uVar2;
  undefined2 uVar3;
  int unaff_gp;
  undefined **ppuVar4;
  undefined1 extraout_var;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  
  cVar1 = *(char *)(unaff_gp + -0x5bbe);
  uVar2 = *(ushort *)(unaff_gp + -0x5c3c);
  uVar3 = *(undefined2 *)(unaff_gp + -0x5c86);
  iVar5 = FUN_00083a80();
  iVar6 = FUN_00036b8c();
  iVar7 = FUN_00036ba8();
  iVar8 = FUN_00037122();
  iVar9 = FUN_00037106();
  if ((((DAT_fef00dcf <= DAT_00167104) && (iVar5 == 1)) && (cVar1 == '\x01')) ||
     (((iVar8 != 1 && (iVar9 != 1)) &&
      ((((uVar2 < DAT_00166ff2 ||
         ((_DAT_fef02622 < DAT_00166ff8 || (*(ushort *)(unaff_gp + -0x5c10) < DAT_00166ff8)))) ||
        (iVar6 != 0)) || (iVar7 != 0)))))) {
    DAT_febf603c = 0x80;
    return;
  }
  if (cVar1 != '\x01') {
    if (cVar1 == '\b') {
      ppuVar4 = &PTR_DAT_001575dc;
      goto LAB_0004c7b0;
    }
    if (cVar1 == '\x10') {
      ppuVar4 = (undefined **)&DAT_001575f0;
      goto LAB_0004c7b0;
    }
    if (cVar1 == ' ') {
      ppuVar4 = (undefined **)&DAT_00157604;
      goto LAB_0004c7b0;
    }
    if (cVar1 != '@') {
      DAT_febf603c = 0x80;
      return;
    }
  }
  ppuVar4 = (undefined **)&DAT_00157618;
LAB_0004c7b0:
  FUN_000a1fca(ppuVar4,uVar3);
  DAT_febf603c = extraout_var;
  return;
}


// ===== FUNCTION 0x4ce5a (FUN_0004ce48) =====

void FUN_0004ce48(void)

{
  int unaff_gp;
  undefined2 uVar1;
  undefined1 extraout_var;
  int iVar2;
  
  iVar2 = FUN_00036b38();
  uVar1 = 0;
  if (iVar2 != 1) {
    uVar1 = *(undefined2 *)(unaff_gp + -0x5c40);
  }
  FUN_000a1fca(&DAT_001563c4,uVar1);
  *(undefined1 *)(unaff_gp + -0x60b5) = extraout_var;
  return;
}


// ===== FUNCTION 0x507da (FUN_000507d2) =====

void FUN_000507d2(undefined2 param_1)

{
  undefined1 extraout_var;
  
  FUN_000a1fca(&PTR_DAT_00156428,param_1);
  DAT_febf6036 = extraout_var;
  return;
}


// ===== FUNCTION 0x507ba (FUN_000507b2) =====

void FUN_000507b2(undefined2 param_1)

{
  undefined1 extraout_var;
  
  FUN_000a1fca(&PTR_DAT_00156414,param_1);
  DAT_febf6035 = extraout_var;
  return;
}


// ===== FUNCTION 0x4ef00 (FUN_0004eef4) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0004eef4(undefined1 param_1,undefined2 param_2)

{
  _DAT_febf6016 = FUN_000a201e(&PTR_LAB_0015698c,param_1,param_2);
  return;
}


// ===== FUNCTION 0x4ef22 (FUN_0004ef16) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0004ef16(undefined1 param_1,undefined2 param_2)

{
  _DAT_febf6018 = FUN_000a201e(&PTR_LAB_001569bc,param_1,param_2);
  return;
}


// ===== FUNCTION 0x4eecc (FUN_0004eeb2) =====

void FUN_0004eeb2(void)

{
  int unaff_gp;
  undefined **ppuVar1;
  undefined1 extraout_var;
  
  if ((DAT_fef00e87 & 1) == 0) {
    ppuVar1 = &PTR_DAT_001563ec;
  }
  else {
    ppuVar1 = &PTR_DAT_00156400;
  }
  FUN_000a1fca(ppuVar1,*(undefined1 *)(unaff_gp + -0x5bc0));
  DAT_febf6033 = extraout_var;
  return;
}


// ===== FUNCTION 0x4c890 (FUN_0004c85c) =====

void FUN_0004c85c(undefined2 param_1)

{
  char cVar1;
  int unaff_gp;
  undefined *puVar2;
  undefined1 extraout_var;
  
  cVar1 = *(char *)(unaff_gp + -0x5bbe);
  if (cVar1 == '\x01') {
    puVar2 = &DAT_001576a0;
  }
  else if (cVar1 == '\x02') {
    puVar2 = &DAT_001576d0;
  }
  else if (cVar1 == '\x04') {
    puVar2 = &DAT_00157700;
  }
  else if (cVar1 == '\b') {
    puVar2 = &DAT_00157730;
  }
  else if (cVar1 == '\x10') {
    puVar2 = &DAT_00157760;
  }
  else if (cVar1 == ' ') {
    puVar2 = &DAT_00157790;
  }
  else {
    puVar2 = &DAT_001577c0;
  }
  FUN_000a201e(puVar2,*(undefined2 *)(unaff_gp + -0x5c86),param_1);
  DAT_fef00dd1 = extraout_var;
  return;
}


// ===== FUNCTION 0x4c8a0 (FUN_0004c85c) =====

void FUN_0004c85c(undefined2 param_1)

{
  char cVar1;
  int unaff_gp;
  undefined *puVar2;
  undefined1 extraout_var;
  
  cVar1 = *(char *)(unaff_gp + -0x5bbe);
  if (cVar1 == '\x01') {
    puVar2 = &DAT_001576a0;
  }
  else if (cVar1 == '\x02') {
    puVar2 = &DAT_001576d0;
  }
  else if (cVar1 == '\x04') {
    puVar2 = &DAT_00157700;
  }
  else if (cVar1 == '\b') {
    puVar2 = &DAT_00157730;
  }
  else if (cVar1 == '\x10') {
    puVar2 = &DAT_00157760;
  }
  else if (cVar1 == ' ') {
    puVar2 = &DAT_00157790;
  }
  else {
    puVar2 = &DAT_001577c0;
  }
  FUN_000a201e(puVar2,*(undefined2 *)(unaff_gp + -0x5c86),param_1);
  DAT_fef00dd1 = extraout_var;
  return;
}


// ===== FUNCTION 0x4c8b8 (FUN_0004c85c) =====

void FUN_0004c85c(undefined2 param_1)

{
  char cVar1;
  int unaff_gp;
  undefined *puVar2;
  undefined1 extraout_var;
  
  cVar1 = *(char *)(unaff_gp + -0x5bbe);
  if (cVar1 == '\x01') {
    puVar2 = &DAT_001576a0;
  }
  else if (cVar1 == '\x02') {
    puVar2 = &DAT_001576d0;
  }
  else if (cVar1 == '\x04') {
    puVar2 = &DAT_00157700;
  }
  else if (cVar1 == '\b') {
    puVar2 = &DAT_00157730;
  }
  else if (cVar1 == '\x10') {
    puVar2 = &DAT_00157760;
  }
  else if (cVar1 == ' ') {
    puVar2 = &DAT_00157790;
  }
  else {
    puVar2 = &DAT_001577c0;
  }
  FUN_000a201e(puVar2,*(undefined2 *)(unaff_gp + -0x5c86),param_1);
  DAT_fef00dd1 = extraout_var;
  return;
}


// ===== FUNCTION 0x4f6e8 (FUN_0004f6ce) =====

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0004f6ce(void)

{
  int unaff_gp;
  undefined *puVar1;
  
  if ((*(byte *)(unaff_gp + -0x5fb4) & 4) == 0) {
    puVar1 = &DAT_00156b10;
  }
  else {
    puVar1 = &DAT_00156b2c;
  }
  _DAT_febf6022 =
       FUN_000a201e(puVar1,*(undefined2 *)(unaff_gp + -0x5c3c),*(undefined2 *)(unaff_gp + -0x5c86));
  return;
}

