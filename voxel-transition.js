(() => {
  'use strict';

  const MAX_VOXELS = 3600;
  const TRANSITION_DURATION = 1800;
  const PHASES = {
    fadeOutEnd: 0.22,
    burstEnd: 0.58,
    holdEnd: 0.70,
    morphEnd: 0.94
  };
  const PAGE_FADE_DURATION = 520;

  const endpoints = {
    farmion: {
      fromView: 'studio-view',
      fromImage: '#studio-view .logo',
      fromData: 'logo',
      toView: 'farmion-view',
      toImage: '#farmion-view .farm-logo-img',
      toData: 'farmion'
    },
    studio: {
      fromView: 'farmion-view',
      fromImage: '#farmion-view .farm-logo-img',
      fromData: 'farmion',
      toView: 'studio-view',
      toImage: '#studio-view .logo',
      toData: 'logo'
    }
  };

  const canvas = document.getElementById('voxel-canvas');
  const studioView = document.getElementById('studio-view');
  const farmionView = document.getElementById('farmion-view');
  let renderer = null;
  let scene = null;
  let camera = null;
  let instancedMesh = null;
  let material = null;
  let geometry = null;
  let dummy = null;
  let isTransitioning = false;

  function getView(viewId) {
    return document.getElementById(viewId);
  }

  function getImage(selector) {
    return document.querySelector(selector);
  }

  function setViewState(view, visible, opacity) {
    if (!view) {
      return;
    }

    view.style.transition = 'none';
    view.style.display = visible ? (view === studioView ? 'flex' : 'block') : 'none';
    view.style.opacity = String(opacity);
    view.style.pointerEvents = visible && opacity > 0.99 ? 'auto' : 'none';
  }

  function updateBrowserState(viewName) {
    const favicon = document.getElementById('site-favicon');
    document.title = viewName === 'farmion'
      ? 'Farmion | Baer & Hoggo Games'
      : 'Baer & Hoggo Games | Farmion';
    if (favicon) {
      favicon.href = viewName === 'farmion' ? 'assets/chicken.png' : 'assets/bh-icon.png';
    }
    const farmionHash = window.location.hash.toLowerCase().startsWith('#farmion')
      ? window.location.hash
      : '#farmion';
    const nextUrl = viewName === 'farmion'
      ? `${window.location.pathname}${window.location.search}${farmionHash}`
      : `${window.location.pathname}${window.location.search}`;
    const desiredHash = viewName === 'farmion' ? farmionHash : '';
    if (window.location.hash !== desiredHash) {
      window.history.replaceState(null, '', nextUrl);
    }
  }

  function switchDOMView(viewName, reveal = true) {
    const nextView = viewName === 'farmion' ? farmionView : studioView;
    const otherView = nextView === farmionView ? studioView : farmionView;
    setViewState(otherView, false, 0);
    setViewState(nextView, true, reveal ? 0 : 1);
    updateBrowserState(viewName);

    if (reveal) {
      window.requestAnimationFrame(() => {
        nextView.style.transition = 'opacity 0.32s ease';
        nextView.style.opacity = '1';
        nextView.style.pointerEvents = 'auto';
      });
    }
  }

  function initThree() {
    if (!window.THREE || !canvas || renderer) {
      return Boolean(renderer);
    }

    const THREE = window.THREE;
    renderer = new THREE.WebGLRenderer({
      canvas,
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance'
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(window.innerWidth, window.innerHeight, false);
    renderer.setClearColor(0x000000, 0);

    scene = new THREE.Scene();
    camera = new THREE.OrthographicCamera(
      -window.innerWidth / 2,
      window.innerWidth / 2,
      window.innerHeight / 2,
      -window.innerHeight / 2,
      0.1,
      2000
    );
    camera.position.z = 1000;

    geometry = new THREE.BoxGeometry(1, 1, 1);
    material = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      // InstancedMesh supplies colors through instanceColor. The cube itself
      // has no per-vertex color attribute, so enabling vertexColors here would
      // multiply every instance by the missing attribute and render black.
      vertexColors: false,
      transparent: true,
      opacity: 1
    });
    instancedMesh = new THREE.InstancedMesh(geometry, material, MAX_VOXELS);

    // Three r128 chooses the instanced-color shader on its first render only
    // when instanceColor already exists. Seed it before the first render.
    instancedMesh.setColorAt(0, new THREE.Color(0xffffff));
    instancedMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    if (instancedMesh.instanceColor) {
      instancedMesh.instanceColor.setUsage(THREE.DynamicDrawUsage);
      instancedMesh.instanceColor.needsUpdate = true;
    }
    material.needsUpdate = true;
    instancedMesh.count = 0;
    scene.add(instancedMesh);
    dummy = new THREE.Object3D();

    window.addEventListener('resize', resizeRenderer);
    return true;
  }

  function resizeRenderer() {
    if (!renderer || !camera) {
      return;
    }

    const width = window.innerWidth;
    const height = window.innerHeight;
    renderer.setSize(width, height, false);
    camera.left = -width / 2;
    camera.right = width / 2;
    camera.top = height / 2;
    camera.bottom = -height / 2;
    camera.updateProjectionMatrix();
  }

  function waitForFrame() {
    return new Promise((resolve) => window.requestAnimationFrame(resolve));
  }

  async function waitForStableLayout() {
    await waitForFrame();
    await waitForFrame();
  }

  function jumpToTop() {
    const root = document.documentElement;
    const previousScrollBehavior = root.style.scrollBehavior;
    // The site enables smooth scrolling globally. Disable it for the
    // measurement jump so phone browser scroll settling cannot offset voxels.
    root.style.scrollBehavior = 'auto';
    window.scrollTo(0, 0);
    root.style.scrollBehavior = previousScrollBehavior;
  }

  async function waitForImage(image) {
    if (!image) {
      throw new Error('Voxel transition image was not found.');
    }
    if (!image.complete || !image.naturalWidth) {
      await new Promise((resolve, reject) => {
        const onLoad = () => {
          image.removeEventListener('load', onLoad);
          image.removeEventListener('error', onError);
          resolve();
        };
        const onError = () => {
          image.removeEventListener('load', onLoad);
          image.removeEventListener('error', onError);
          reject(new Error(`Unable to load ${image.currentSrc || image.src}.`));
        };
        image.addEventListener('load', onLoad, { once: true });
        image.addEventListener('error', onError, { once: true });
      });
    }
    if (typeof image.decode === 'function') {
      await image.decode().catch(() => undefined);
    }
  }

  function sampleBakedImage(image, dataKey) {
    const baked = window.VOXEL_IMAGE_DATA && window.VOXEL_IMAGE_DATA[dataKey];
    if (!baked || !Array.isArray(baked.points) || !baked.points.length) {
      return [];
    }

    const rect = image.getBoundingClientRect();
    if (!rect.width || !rect.height) {
      return [];
    }

    const THREE = window.THREE;
    return baked.points.map(([x, y, size, color]) => ({
      x: rect.left + (x / 65535) * rect.width,
      y: rect.top + (y / 65535) * rect.height,
      size: Math.max(2, (size / 65535) * rect.width),
      color: new THREE.Color(color)
    }));
  }

  function sampleCanvasImage(image) {
    const width = image.naturalWidth;
    const height = image.naturalHeight;
    const sourceCanvas = document.createElement('canvas');
    sourceCanvas.width = width;
    sourceCanvas.height = height;
    const context = sourceCanvas.getContext('2d', { willReadFrequently: true });
    context.drawImage(image, 0, 0, width, height);
    const pixels = context.getImageData(0, 0, width, height).data;
    const cell = Math.max(4, Math.ceil(Math.sqrt((width * height) / MAX_VOXELS)));
    const rect = image.getBoundingClientRect();
    const points = [];

    for (let y = 0; y < height; y += cell) {
      for (let x = 0; x < width; x += cell) {
        const sampleX = Math.min(width - 1, x + Math.floor(cell / 2));
        const sampleY = Math.min(height - 1, y + Math.floor(cell / 2));
        const offset = (sampleY * width + sampleX) * 4;
        const alpha = pixels[offset + 3];
        if (alpha < 24) {
          continue;
        }
        points.push({
          x: rect.left + ((x + cell / 2) / width) * rect.width,
          y: rect.top + ((y + cell / 2) / height) * rect.height,
          size: Math.max(2, (cell / width) * rect.width),
          color: new window.THREE.Color(
            (pixels[offset] << 16) | (pixels[offset + 1] << 8) | pixels[offset + 2]
          )
        });
      }
    }
    return points;
  }

  async function sampleImage(image, dataKey) {
    await waitForImage(image);
    try {
      const livePoints = sampleCanvasImage(image);
      if (livePoints.length) {
        return livePoints;
      }
    } catch (error) {
      // Local file pages taint a canvas in Chromium. The baked data is the
      // intentional path for that environment, so only fail if it is absent.
      const bakedPoints = sampleBakedImage(image, dataKey);
      if (bakedPoints.length) {
        return bakedPoints;
      }
      throw new Error(`Browser blocked pixel sampling for ${image.src}.`, { cause: error });
    }

    const bakedPoints = sampleBakedImage(image, dataKey);
    if (!bakedPoints.length) {
      throw new Error(`No voxel pixels were found for ${image.src}.`);
    }
    return bakedPoints;
  }

  function resizePointSet(points, count) {
    return Array.from({ length: count }, (_, index) => points[Math.floor(index * points.length / count)]);
  }

  async function buildImageVoxels(viewName) {
    const endpoint = endpoints[viewName];
    const fromView = getView(endpoint.fromView);
    const targetView = getView(endpoint.toView);
    const fromImage = getImage(endpoint.fromImage);
    const targetImage = getImage(endpoint.toImage);
    if (!endpoint || !fromView || !targetView || !fromImage || !targetImage) {
      throw new Error(`Voxel transition endpoint is incomplete for ${viewName}.`);
    }

    jumpToTop();
    setViewState(fromView, true, 1);
    setViewState(targetView, false, 0);
    fromImage.style.transition = 'none';
    fromImage.style.opacity = '1';
    targetImage.style.transition = 'none';
    targetImage.style.opacity = '1';
    await waitForStableLayout();
    const fromPoints = await sampleImage(fromImage, endpoint.fromData);

    setViewState(fromView, false, 0);
    // Keep the measurement layout mounted but transparent. Making it opaque
    // here causes a visible destination-page flash before the canvas starts.
    setViewState(targetView, true, 0);
    await waitForStableLayout();
    const targetPoints = await sampleImage(targetImage, endpoint.toData);
    if (!fromPoints.length || !targetPoints.length) {
      throw new Error('Voxel transition images produced no sample points.');
    }

    const count = Math.min(MAX_VOXELS, Math.max(fromPoints.length, targetPoints.length));
    const resizedFrom = resizePointSet(fromPoints, count);
    const resizedTarget = resizePointSet(targetPoints, count);
    const voxels = resizedFrom.map((from, index) => {
      const target = resizedTarget[index];
      const angle = index * 2.399963 + 0.8;
      const radius = 90 + (index % 13) * 10;
      return {
        fromX: from.x,
        fromY: from.y,
        fromSize: from.size,
        fromColor: from.color.clone(),
        toX: target.x,
        toY: target.y,
        toSize: target.size,
        toColor: target.color.clone(),
        arcX: Math.cos(angle) * radius,
        arcY: Math.sin(angle) * radius,
        arcZ: 120 + (index % 9) * 22,
        spin: ((index % 7) - 3) * 0.9
      };
    });

    setViewState(fromView, true, 1);
    setViewState(targetView, false, 0);
    targetImage.style.transition = 'none';
    targetImage.style.opacity = '0';
    return { voxels, fromView, targetView, targetImage };
  }

  function easeOutCubic(value) {
    return 1 - Math.pow(1 - value, 3);
  }

  function easeInCubic(value) {
    return value * value * value;
  }

  function easeInOutCubic(value) {
    return value < 0.5
      ? 4 * value * value * value
      : 1 - Math.pow(-2 * value + 2, 3) / 2;
  }

  function lerp(start, end, amount) {
    return start + (end - start) * amount;
  }

  function renderVoxels(voxels, progress, refinement = 0) {
    if (!renderer || !camera || !instancedMesh || !dummy) {
      return;
    }

    const width = window.innerWidth;
    const height = window.innerHeight;
    const burstAmount = Math.max(0, Math.min(1,
      (progress - PHASES.fadeOutEnd) / (PHASES.burstEnd - PHASES.fadeOutEnd)
    ));
    // Start with a restrained burst so the source logo remains readable as it
    // becomes voxels, then let the last part of the burst open up quickly.
    const burstProgress = easeInCubic(burstAmount);
    const morphAmount = Math.max(0, Math.min(1,
      (progress - PHASES.holdEnd) / (PHASES.morphEnd - PHASES.holdEnd)
    ));
    const morphProgress = easeInOutCubic(morphAmount);
    const holdAmount = Math.max(0, Math.min(1,
      (progress - PHASES.burstEnd) / (PHASES.holdEnd - PHASES.burstEnd)
    ));
    // A soft sine envelope makes the voxels keep floating after the burst,
    // while returning to the exact burst positions before the morph begins.
    const holdMotion = Math.sin(Math.PI * holdAmount);
    const motionTime = performance.now() * 0.0018;
    const colorProgress = progress < PHASES.burstEnd
      ? 0.22 * burstProgress
      : progress < PHASES.holdEnd
        ? 0.22
        : 0.22 + 0.78 * easeOutCubic(morphAmount);
    const refinementAmount = Math.max(0, Math.min(1, refinement));
    material.opacity = 1 - refinementAmount;

    voxels.forEach((voxel, index) => {
      let x = voxel.fromX;
      let y = voxel.fromY;
      let z = 0;
      let size = voxel.fromSize;
      let rotation = 0;

      if (progress >= PHASES.fadeOutEnd && progress < PHASES.burstEnd) {
        x += voxel.arcX * 1.5 * burstProgress;
        y += voxel.arcY * 1.5 * burstProgress;
        z = voxel.arcZ * 1.25 * burstProgress;
        size *= 1 + 0.12 * burstProgress;
        rotation = voxel.spin * burstProgress;
      } else if (progress >= PHASES.burstEnd && progress < PHASES.holdEnd) {
        const burstX = voxel.fromX + voxel.arcX * 1.5;
        const burstY = voxel.fromY + voxel.arcY * 1.5;
        const burstZ = voxel.arcZ * 1.25;
        const phase = index * 0.73;
        const sway = Math.sin(motionTime * (1.4 + (index % 3) * 0.12) + phase);
        const bob = Math.cos(motionTime * (1.1 + (index % 4) * 0.08) + phase * 1.3);
        x = burstX + sway * (5 + (index % 4)) * holdMotion;
        y = burstY + bob * (4 + (index % 3)) * holdMotion;
        z = burstZ + Math.sin(motionTime * 1.7 + phase) * 12 * holdMotion;
        size = voxel.fromSize * 1.12 * (1 + sway * 0.035 * holdMotion);
        rotation = voxel.spin + sway * 0.08 * holdMotion;
      } else if (progress >= PHASES.holdEnd && progress < PHASES.morphEnd) {
        x = lerp(voxel.fromX + voxel.arcX * 1.5, voxel.toX, morphProgress);
        y = lerp(voxel.fromY + voxel.arcY * 1.5, voxel.toY, morphProgress);
        z = lerp(voxel.arcZ * 1.25, 0, morphProgress);
        size = lerp(voxel.fromSize * 1.12, voxel.toSize, morphProgress);
        rotation = voxel.spin * (1 - morphProgress);
      } else if (progress >= PHASES.morphEnd) {
        x = voxel.toX;
        y = voxel.toY;
        // During the final page fade, reveal more of the crisp image between
        // progressively smaller, lighter voxels instead of dropping the
        // chunky target representation all at once.
        size = lerp(voxel.toSize, Math.max(1.25, voxel.toSize * 0.35), refinementAmount);
      }

      dummy.position.set(x - width / 2, height / 2 - y, z);
      dummy.scale.set(size, size, size);
      dummy.rotation.set(rotation * 0.65, rotation, rotation);
      dummy.updateMatrix();
      instancedMesh.setMatrixAt(index, dummy.matrix);
      instancedMesh.setColorAt(index, voxel.fromColor.clone().lerp(voxel.toColor, colorProgress));
    });
    instancedMesh.count = voxels.length;
    instancedMesh.instanceMatrix.needsUpdate = true;
    instancedMesh.instanceColor.needsUpdate = true;
    renderer.render(scene, camera);
  }

  function fadeViewIn(view, onProgress) {
    return new Promise((resolve, reject) => {
      view.style.transition = 'none';
      view.style.opacity = '0';
      view.style.pointerEvents = 'none';
      const startedAt = performance.now();

      // One bounded frame loop owns both fades and their completion. No final
      // voxel callback may repaint the canvas after transition cleanup.
      const frame = (now) => {
        try {
          const progress = Math.min(1, (now - startedAt) / PAGE_FADE_DURATION);
          view.style.opacity = String(easeOutCubic(progress));
          onProgress(progress);
          if (progress < 1) {
            window.requestAnimationFrame(frame);
          } else {
            view.style.opacity = '1';
            view.style.pointerEvents = 'auto';
            resolve();
          }
        } catch (error) {
          reject(error);
        }
      };
      window.requestAnimationFrame(frame);
    });
  }

  async function animateVoxels(transition, viewName) {
    await new Promise((resolve, reject) => {
      const startedAt = performance.now();
      let targetMounted = false;
      const frame = (now) => {
        try {
          const progress = Math.min(1, (now - startedAt) / TRANSITION_DURATION);
          const sourceFade = progress < PHASES.fadeOutEnd
            ? 1 - easeOutCubic(progress / PHASES.fadeOutEnd)
            : 0;
          transition.fromView.style.opacity = String(sourceFade);
          transition.fromView.style.pointerEvents = 'none';
          if (!targetMounted && progress >= PHASES.burstEnd) {
            targetMounted = true;
            setViewState(transition.targetView, true, 0);
            transition.targetImage.style.opacity = '0';
          }
          renderVoxels(transition.voxels, progress);
          if (progress < 1) {
            window.requestAnimationFrame(frame);
          } else {
            resolve();
          }
        } catch (error) {
          reject(error);
        }
      };
      window.requestAnimationFrame(frame);
    });

    transition.fromView.style.display = 'none';
    transition.targetImage.style.transition = 'none';
    transition.targetImage.style.opacity = '1';
    await fadeViewIn(transition.targetView, (progress) => {
      renderVoxels(transition.voxels, 1, progress);
    });
    updateBrowserState(viewName);
  }

  function clearVoxels() {
    if (material) {
      material.opacity = 0;
    }
    if (instancedMesh) {
      instancedMesh.count = 0;
      instancedMesh.instanceMatrix.needsUpdate = true;
      if (instancedMesh.instanceColor) {
        instancedMesh.instanceColor.needsUpdate = true;
      }
    }
    // Reset the rendered frame as well as the mesh, including on error paths.
    if (renderer) {
      renderer.clear();
    }
  }

  async function triggerVoxelTransition(viewName) {
    if (isTransitioning || !endpoints[viewName]) {
      return;
    }

    isTransitioning = true;
    try {
      if (!initThree()) {
        switchDOMView(viewName);
        return;
      }
      const transition = await buildImageVoxels(viewName);
      canvas.classList.add('active');
      await animateVoxels(transition, viewName);
    } catch (error) {
      console.error('Voxel image transition failed.', error);
      const endpoint = endpoints[viewName];
      const targetView = getView(endpoint.toView);
      const targetImage = getImage(endpoint.toImage);
      if (targetImage) {
        targetImage.style.transition = 'none';
        targetImage.style.opacity = '1';
      }
      switchDOMView(viewName);
      if (targetView) {
        targetView.style.opacity = '1';
      }
    } finally {
      clearVoxels();
      canvas.classList.remove('active');
      isTransitioning = false;
    }
  }

  window.triggerVoxelTransition = triggerVoxelTransition;

  document.addEventListener('DOMContentLoaded', () => {
    initThree();

    document.getElementById('btn-discover-farmion')?.addEventListener('click', () => {
      triggerVoxelTransition('farmion');
    });
    if (window.location.hash.toLowerCase().startsWith('#farmion')) {
      switchDOMView('farmion', false);
      const section = document.getElementById(window.location.hash.slice(1));
      if (section) {
        window.requestAnimationFrame(() => section.scrollIntoView({ behavior: 'instant' }));
      }
    } else {
      switchDOMView('studio', false);
    }
  });
})();
