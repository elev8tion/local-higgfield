import { listBackendModels } from './localapi.js';
import {
  getAspectRatiosForI2IModel,
  getAspectRatiosForI2VModel,
  getAspectRatiosForModel,
  getAspectRatiosForVideoModel,
  getDurationsForI2VModel,
  getDurationsForModel,
  getI2VModelById,
  getI2IModelById,
  getLipSyncModelById,
  getMaxImagesForI2IModel,
  getModelById,
  getModesForModel,
  getQualityFieldForI2IModel,
  getQualityFieldForModel,
  getResolutionsForI2IModel,
  getResolutionsForI2VModel,
  getResolutionsForLipSyncModel,
  getResolutionsForModel,
  getResolutionsForVideoModel,
  i2iModels,
  i2vModels,
  imageLipSyncModels,
  lipsyncModels,
  t2iModels,
  t2vModels,
  v2vModels,
  videoLipSyncModels,
} from './models.js';

let backendCatalogPromise = null;
let backendCatalogCache = null;

export async function loadBackendModelCatalog() {
  if (!backendCatalogPromise) {
    backendCatalogPromise = listBackendModels()
      .then((catalog) => {
        backendCatalogCache = catalog;
        return catalog;
      })
      .catch((error) => {
        backendCatalogPromise = null;
        throw error;
      });
  }
  return backendCatalogPromise;
}

export function getCachedBackendModelCatalog() {
  return backendCatalogCache;
}

export function getBackendModelsByCategory(category) {
  return backendCatalogCache?.models?.filter((model) => model.category === category) || [];
}

export function getImageGenerationModels() {
  return t2iModels;
}

export function getImageTransformModels() {
  return i2iModels;
}

export function getVideoGenerationModels() {
  return t2vModels;
}

export function getImageToVideoModels() {
  return i2vModels;
}

export function getWorkerReadyImageToVideoModels() {
  return i2vModels.filter((model) => model.id === 'wan2.2-image-to-video');
}

export function getVideoTransformModels() {
  return v2vModels;
}

export function getCurrentVideoModels({ imageMode = false, v2vMode = false } = {}) {
  if (v2vMode) return getVideoTransformModels();
  if (imageMode) return getImageToVideoModels();
  return getVideoGenerationModels();
}

export function getDefaultVideoModel({ imageMode = false, v2vMode = false } = {}) {
  return getCurrentVideoModels({ imageMode, v2vMode })[0];
}

export function getLipsyncImageModels() {
  return imageLipSyncModels;
}

export function getLipsyncVideoModels() {
  return videoLipSyncModels;
}

export function getWorkerReadyLipSyncVideoModels() {
  return videoLipSyncModels.filter((model) => model.id === 'latent-sync');
}

export function getCurrentLipSyncModels(inputMode = 'image') {
  return inputMode === 'image' ? getLipsyncImageModels() : getLipsyncVideoModels();
}

export function getDefaultLipSyncModel(inputMode = 'image') {
  return getCurrentLipSyncModels(inputMode)[0];
}

export {
  lipsyncModels,
  getModelById,
  getI2IModelById,
  getI2VModelById,
  getLipSyncModelById,
  getAspectRatiosForModel,
  getAspectRatiosForI2IModel,
  getAspectRatiosForI2VModel,
  getAspectRatiosForVideoModel,
  getDurationsForModel,
  getDurationsForI2VModel,
  getResolutionsForModel,
  getResolutionsForI2IModel,
  getResolutionsForI2VModel,
  getResolutionsForVideoModel,
  getResolutionsForLipSyncModel,
  getQualityFieldForModel,
  getQualityFieldForI2IModel,
  getMaxImagesForI2IModel,
  getModesForModel,
};
