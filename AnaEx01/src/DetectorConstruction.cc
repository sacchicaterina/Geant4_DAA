//
// ********************************************************************
// * License and Disclaimer                                           *
// *                                                                  *
// * The  Geant4 software  is  copyright of the Copyright Holders  of *
// * the Geant4 Collaboration.  It is provided  under  the terms  and *
// * conditions of the Geant4 Software License,  included in the file *
// * LICENSE and available at  http://cern.ch/geant4/license .  These *
// * include a list of copyright holders.                             *
// *                                                                  *
// * Neither the authors of this software system, nor their employing *
// * institutes,nor the agencies providing financial support for this *
// * work  make  any representation or  warranty, express or implied, *
// * regarding  this  software system or assume any liability for its *
// * use.  Please see the license in the file  LICENSE  and URL above *
// * for the full disclaimer and the limitation of liability.         *
// *                                                                  *
// * This  code  implementation is the result of  the  scientific and *
// * technical work of the GEANT4 collaboration.                      *
// * By using,  copying,  modifying or  distributing the software (or *
// * any work based  on the software)  you  agree  to acknowledge its *
// * use  in  resulting  scientific  publications,  and indicate your *
// * acceptance of all terms of the Geant4 Software license.          *
// ********************************************************************
//
/// \file DetectorConstruction.cc
/// \brief Implementation of the DetectorConstruction class
//

#include "DetectorConstruction.hh"
#include "DetectorMessenger.hh"

#include "G4Material.hh"
#include "G4NistManager.hh"

#include "G4Box.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4PVReplica.hh"

#include "G4GeometryManager.hh"
#include "G4PhysicalVolumeStore.hh"
#include "G4LogicalVolumeStore.hh"
#include "G4SolidStore.hh"

#include "G4VisAttributes.hh"
#include "G4Colour.hh"
#include "G4SystemOfUnits.hh"
#include "G4RunManager.hh"

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

DetectorConstruction::DetectorConstruction()
    : G4VUserDetectorConstruction(),
      fAbsorberMaterial(0), fGapMaterial(0), fDefaultMaterial(0),
      fSolidWorld(0), fLogicWorld(0), fPhysiWorld(0),
      fSolidCalor(0), fLogicCalor(0), fPhysiCalor(0),
      fSolidLayer(0), fLogicLayer(0), fPhysiLayer(0),
      fSolidAbsorber(0), fLogicAbsorber(0), fPhysiAbsorber(0),
      fSolidGap(0), fLogicGap(0), fPhysiGap(0),
      fDetectorMessenger(0)
{
  fAbsorberThickness = 1. * mm;
  fGapThickness = 0. * mm;
  fNbOfLayers = 300;
  fCalorSizeYZ = 10. * cm;

  ComputeCalorParameters();

  DefineMaterials();
  SetAbsorberMaterial("G4_WATER");
  SetGapMaterial("G4_WATER");

  fDetectorMessenger = new DetectorMessenger(this);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

DetectorConstruction::~DetectorConstruction()
{
  delete fDetectorMessenger;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

G4VPhysicalVolume *DetectorConstruction::Construct()
{
  return ConstructCalorimeter();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void DetectorConstruction::DefineMaterials()
{
  G4NistManager *man = G4NistManager::Instance();

  fDefaultMaterial = man->FindOrBuildMaterial("G4_Galactic");
  man->FindOrBuildMaterial("G4_WATER");

  G4cout << *(G4Material::GetMaterialTable()) << G4endl;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

G4VPhysicalVolume *DetectorConstruction::ConstructCalorimeter()
{
  G4GeometryManager::GetInstance()->OpenGeometry();
  G4PhysicalVolumeStore::GetInstance()->Clean();
  G4LogicalVolumeStore::GetInstance()->Clean();
  G4SolidStore::GetInstance()->Clean();

  ComputeCalorParameters();

  //
  // World
  //
  fSolidWorld = new G4Box("World",
                          fWorldSizeX / 2,
                          fWorldSizeYZ / 2,
                          fWorldSizeYZ / 2);

  fLogicWorld = new G4LogicalVolume(fSolidWorld,
                                    fDefaultMaterial,
                                    "World");

  fPhysiWorld = new G4PVPlacement(0,
                                  G4ThreeVector(),
                                  fLogicWorld,
                                  "World",
                                  0,
                                  false,
                                  0);

  //
  // Calorimeter
  //
  fSolidCalor = 0;
  fLogicCalor = 0;
  fPhysiCalor = 0;
  fSolidLayer = 0;
  fLogicLayer = 0;
  fPhysiLayer = 0;

  if (fCalorThickness > 0.)
  {
    fSolidCalor = new G4Box("Calorimeter",
                            fCalorSizeYZ / 2,
                            fCalorSizeYZ / 2,
                            fCalorThickness / 2);

    fLogicCalor = new G4LogicalVolume(fSolidCalor,
                                      fAbsorberMaterial,
                                      "Calorimeter");

    fPhysiCalor = new G4PVPlacement(0,
                                    G4ThreeVector(),
                                    fLogicCalor,
                                    "Calorimeter",
                                    fLogicWorld,
                                    false,
                                    0);

    //
    // Layer
    //
    fSolidLayer = new G4Box("Layer",
                            fCalorSizeYZ / 2,
                            fCalorSizeYZ / 2,
                            fLayerThickness / 2);

    fLogicLayer = new G4LogicalVolume(fSolidLayer,
                                      fAbsorberMaterial,
                                      "Layer");

    if (fNbOfLayers > 1)
      fPhysiLayer = new G4PVReplica("Layer",
                                    fLogicLayer,
                                    fLogicCalor,
                                    kZAxis,
                                    fNbOfLayers,
                                    fLayerThickness);
    else
      fPhysiLayer = new G4PVPlacement(0,
                                      G4ThreeVector(),
                                      fLogicLayer,
                                      "Layer",
                                      fLogicCalor,
                                      false,
                                      0);
  }

  //
  // Absorber
  //
  fSolidAbsorber = 0;
  fLogicAbsorber = 0;
  fPhysiAbsorber = 0;

  if (fAbsorberThickness > 0.)
  {
    fSolidAbsorber = new G4Box("Absorber",
                               fCalorSizeYZ / 2,
                               fCalorSizeYZ / 2,
                               fAbsorberThickness / 2);

    fLogicAbsorber = new G4LogicalVolume(fSolidAbsorber,
                                         fAbsorberMaterial,
                                         fAbsorberMaterial->GetName());

    fPhysiAbsorber = new G4PVPlacement(0,
                                       G4ThreeVector(0., 0., 0.),
                                       fLogicAbsorber,
                                       fAbsorberMaterial->GetName(),
                                       fLogicLayer,
                                       false,
                                       0);
  }

  //
  // Gap
  //
  fSolidGap = 0;
  fLogicGap = 0;
  fPhysiGap = 0;

  if (fGapThickness > 0.)
  {
    fSolidGap = new G4Box("Gap",
                          fCalorSizeYZ / 2,
                          fCalorSizeYZ / 2,
                          fGapThickness / 2);

    fLogicGap = new G4LogicalVolume(fSolidGap,
                                    fGapMaterial,
                                    fGapMaterial->GetName());

    fPhysiGap = new G4PVPlacement(0,
                                  G4ThreeVector(0., 0., fAbsorberThickness / 2),
                                  fLogicGap,
                                  fGapMaterial->GetName(),
                                  fLogicLayer,
                                  false,
                                  0);
  }

  PrintCalorParameters();

  //
  // Visualization attributes
  //
  fLogicWorld->SetVisAttributes(G4VisAttributes::GetInvisible());

  G4VisAttributes *simpleBoxVisAtt =
      new G4VisAttributes(G4Colour(1.0, 1.0, 1.0));

  simpleBoxVisAtt->SetVisibility(true);
  fLogicCalor->SetVisAttributes(simpleBoxVisAtt);

  return fPhysiWorld;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void DetectorConstruction::PrintCalorParameters()
{
  G4cout << "\n------------------------------------------------------------"
         << "\n---> The calorimeter is " << fNbOfLayers << " layers of: [ "
         << fAbsorberThickness / mm << "mm of " << fAbsorberMaterial->GetName()
         << " + "
         << fGapThickness / mm << "mm of " << fGapMaterial->GetName() << " ] "
         << "\n------------------------------------------------------------\n";
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void DetectorConstruction::SetAbsorberMaterial(G4String materialChoice)
{
  G4Material *pttoMaterial =
      G4NistManager::Instance()->FindOrBuildMaterial(materialChoice);

  if (pttoMaterial)
  {
    fAbsorberMaterial = pttoMaterial;

    if (fLogicAbsorber)
    {
      fLogicAbsorber->SetMaterial(fAbsorberMaterial);
      G4RunManager::GetRunManager()->PhysicsHasBeenModified();
    }
  }
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void DetectorConstruction::SetGapMaterial(G4String materialChoice)
{
  G4Material *pttoMaterial =
      G4NistManager::Instance()->FindOrBuildMaterial(materialChoice);

  if (pttoMaterial)
  {
    fGapMaterial = pttoMaterial;

    if (fLogicGap)
    {
      fLogicGap->SetMaterial(fGapMaterial);
      G4RunManager::GetRunManager()->PhysicsHasBeenModified();
    }
  }
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void DetectorConstruction::SetAbsorberThickness(G4double val)
{
  fAbsorberThickness = val;
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void DetectorConstruction::SetGapThickness(G4double val)
{
  fGapThickness = val;
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void DetectorConstruction::SetCalorSizeYZ(G4double val)
{
  fCalorSizeYZ = val;
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void DetectorConstruction::SetNbOfLayers(G4int val)
{
  fNbOfLayers = val;
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}
