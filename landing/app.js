function initNavigationTheme() {
  const navigation = document.querySelector('.nav');
  if (!navigation) return;
  const surfaces = [...document.querySelectorAll('main > *, body > footer')];
  let currentSurface;
  let frame = 0;

  function backgroundOf(element) {
    while (element) {
      const background = getComputedStyle(element).backgroundColor;
      if (background !== 'transparent' && background !== 'rgba(0, 0, 0, 0)') return background;
      element = element.parentElement;
    }
    return getComputedStyle(document.body).backgroundColor;
  }

  function update(force = false) {
    // Switch as each section crosses the middle of the sticky header.
    const probe = navigation.getBoundingClientRect().height / 2;
    const surface = surfaces.findLast(element => {
      const bounds = element.getBoundingClientRect();
      return bounds.top <= probe && bounds.bottom > probe;
    }) ?? surfaces[0] ?? document.body;
    if (surface === currentSurface && !force) return;
    currentSurface = surface;
    const background = backgroundOf(surface);
    const [red, green, blue] = background.match(/[\d.]+/g).slice(0, 3).map(Number);
    const brightness = (red * 0.2126 + green * 0.7152 + blue * 0.0722) / 255;
    navigation.style.setProperty('--nav-background', background);
    navigation.style.setProperty('--nav-foreground', getComputedStyle(surface).color);
    navigation.dataset.theme = brightness < 0.5 ? 'dark' : 'light';
  }

  function schedule() {
    if (frame) return;
    frame = requestAnimationFrame(() => {
      frame = 0;
      update();
    });
  }

  window.addEventListener('scroll', schedule, {passive: true});
  window.addEventListener('pageshow', () => update(true));
  const resize = new ResizeObserver(() => update(true));
  for (const element of [navigation, ...surfaces]) resize.observe(element);
  update();
}
initNavigationTheme();

const steps = [
  [
    "BEFORE WRITING",
    "Start with a better question.",
    "You confirm the question, who will read the essay, the word count, and the language. The reader's knowledge shapes what the essay needs to explain.",
    "question",
    "Checks the question, reader, language, and a target of at least 500 words.",
    "question.md"
  ],
  [
    "RESEARCH",
    "Have something worth saying.",
    "Research gathers facts, scenes, numbers, and quotes, guided by a skeptic, a newcomer, and an expert. It records the strongest objection and missing facts. Your own records can be sources too.",
    "sources",
    "Requires at least three sources with notes. Fetches web links, checks local paths, and flags access problems for review.",
    "sources.md + research.md"
  ],
  [
    "STRUCTURE",
    "An argument before the prose.",
    "State a thesis that answers the reader's question. Choose a case to follow and a puzzle to resolve, then outline one claim per paragraph. A critic challenges the argument before drafting.",
    "outline",
    "Checks the thesis, the outline length, complete sentences, and referenced source identifiers.",
    "outline.md + outline-review.md"
  ],
  [
    "DRAFTING",
    "Permission to write badly.",
    "One author writes straight through before editing, keeping a consistent voice. A case carries the argument, with at most one named study per paragraph. The draft leaves room to cut.",
    "draft",
    "Checks length from the target to 15% above it, body structure, and mechanical writing patterns. Scientific drafts also need source markers.",
    "draft.md"
  ],
  [
    "DISTANCE",
    "What does a fresh reader remember?",
    "A fresh reader reads the draft once and outlines it from memory. They report where they lost the thread, would have stopped reading, or doubted a claim, and what stayed with them.",
    "recall",
    "Requires one recall sentence per paragraph, in the reader's own words, and all eight sections of the reader report.",
    "reader.md"
  ],
  [
    "SEQUENCING",
    "Every sentence earns the next.",
    "Compare the reader's recall with the intended outline. Build a new outline, then reorder paragraphs and sentences, rebuild points that did not land, and cut what the reader skipped.",
    "outline2",
    "Checks the new outline, one draft paragraph per point, and draft length from the target to 15% above it.",
    "outline-2.md + draft-2.md"
  ],
  [
    "REWRITING",
    "Revise where it makes a difference.",
    "An editor marks up to 25 flawed spans. Each gets three distinct alternatives or a reason to keep it. Apply the chosen edits, check the surrounding sentences, and add a title.",
    "rewrite + final",
    "Checks each edit's alternatives or rejection reason and chosen text. The final essay must land between 90% and 100% of the target.",
    "edits.md + rewrites.md + final.md"
  ],
  [
    "FACT-CHECKING",
    "Every claim answers to the notes.",
    "A fact-checker reviews numbers, names, results, quotes, and causal claims against the source notes. Each is marked supported, fixed, or cut. This pass changes facts without restyling the prose.",
    "facts + final",
    "Checks recorded verdicts, source identifiers, and supported claims in the essay, then rechecks the final text and its length.",
    "facts.md + final.md"
  ],
  [
    "CRITIQUE",
    "Can it be better?",
    "A second fresh reader checks what the finished essay communicates and where they would stop. Fix the remaining problems in one final pass, then report sources, fact-check changes, gaps, and doubts.",
    "final",
    "Rechecks title, length, quotations against source notes, and mechanical writing patterns. Scientific essays also need citations and references.",
    "reader-2.md + final.md"
  ]
];
const samples = [
  [
    "A question to give the essay direction.",
    "Question: What makes an argument convincing?\nReader: A curious reader with no formal training\nWords: 1500\nLanguage: en"
  ],
  [
    "The sources, notes, and origins of each idea.",
    "## source-id\nLink: <URL, DOI, local path, or conversation>\nNotes:\n<Facts, scenes, numbers, and verbatim quotes.>"
  ],
  [
    "Alternatives for each flawed span stay on record.",
    '### 1\nSpan: "<the exact flawed span>"\n- v1: <a clearer version>\n- v2: <a different structure>\n- v3: <another way to build the idea>\nChosen: <the selected version>\n\n<Or Rejected: followed by the reason to keep it.>'
  ],
  [
    "The finished essay, revised and fact-checked.",
    "# <A title of at most eight words>\n\n<Revised paragraphs following the new outline.>\n<Claims checked against the source notes.>\n\n<The scientific edition also adds citations\nand a reference list in your chosen style.>"
  ]
];

function tabs(selector, activate) {
  const buttons = [...document.querySelectorAll(selector)];
  function select(index, focus = false, automatic = false) {
    buttons.forEach((button, i) => {
      button.setAttribute('aria-selected', String(i === index));
      button.tabIndex = i === index ? 0 : -1;
    });
    activate(buttons[index], index, automatic);
    if (focus) buttons[index].focus();
  }
  buttons.forEach((button, index) => {
    button.addEventListener('click', () => select(index));
    button.addEventListener('keydown', event => {
      const actions = {ArrowDown: (index + 1) % buttons.length, ArrowRight: (index + 1) % buttons.length, ArrowUp: (index - 1 + buttons.length) % buttons.length, ArrowLeft: (index - 1 + buttons.length) % buttons.length, Home: 0, End: buttons.length - 1};
      if (Object.hasOwn(actions, event.key)) {event.preventDefault(); select(actions[event.key], true);}
    });
  });
  return select;
}
const stepMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let stepAnimations = [];
let previousStep = 0;
function stopStepAnimations() {
  stepAnimations.forEach(animation => animation.cancel());
  stepAnimations = [];
}
stepMotion.addEventListener('change', stopStepAnimations);
tabs('[data-step]', (button, index) => {
  if (index === previousStep) return;
  stopStepAnimations();
  const direction = index < previousStep ? -1 : 1;
  previousStep = index;
  const [category, title, description, gate, gateDescription, file] = steps[index];
  for (const [id, value] of Object.entries({'step-category': category, 'step-counter': `${String(index + 1).padStart(2, '0')} / ${String(steps.length).padStart(2, '0')}`, 'large-step': String(index + 1).padStart(2, '0'), 'step-title': title, 'step-description': description, 'gate-name': gate, 'gate-description': gateDescription, 'step-file': file})) document.getElementById(id).textContent = value;
  const panel = document.getElementById('step-panel');
  panel.setAttribute('aria-labelledby', button.id);
  if (stepMotion.matches) return;

  stepAnimations.push(panel.animate([
    {opacity: 0.75, transform: `translateY(${direction * 5}px)`, borderColor: '#b3bea8'},
    {opacity: 1, transform: 'translateY(0)', borderColor: '#d8dcce'}
  ], {duration: 380, easing: 'cubic-bezier(.22,1,.36,1)'}));

  const section = panel.closest('.method');
  const pulse = section.querySelector('.method-pulse');
  const sectionBounds = section.getBoundingClientRect();
  const cardBounds = panel.parentElement.getBoundingClientRect();
  const originX = cardBounds.left - sectionBounds.left + cardBounds.width / 2;
  const originY = cardBounds.top - sectionBounds.top + cardBounds.height / 2;
  const diameter = Math.min(cardBounds.width, cardBounds.height);
  const farthestCorner = Math.hypot(
    Math.max(originX, sectionBounds.width - originX),
    Math.max(originY, sectionBounds.height - originY),
  );
  const reach = 2 * farthestCorner / diameter * 1.08;
  for (const [name, value] of Object.entries({
    '--pulse-x': originX, '--pulse-y': originY,
    '--pulse-width': diameter, '--pulse-height': diameter,
  })) pulse.style.setProperty(name, `${value}px`);

  stepAnimations.push(pulse.querySelector('.method-pulse-wash').animate([
    {opacity: 0}, {opacity: 0.35, offset: 0.2}, {opacity: 0},
  ], {duration: 2900, easing: 'ease-out'}));
  pulse.querySelectorAll(':scope > span').forEach((wave, index) => {
    stepAnimations.push(wave.animate([
      {transform: 'translate(-50%, -50%) scale(1)', opacity: 0, offset: 0},
      {transform: 'translate(-50%, -50%) scale(1.08)', opacity: 0.5, offset: 0.08},
      {transform: `translate(-50%, -50%) scale(${reach * 0.86})`, opacity: 0.16, offset: 0.85},
      {transform: `translate(-50%, -50%) scale(${reach})`, opacity: 0, offset: 1},
    ], {duration: 2500, delay: index * 220, easing: 'cubic-bezier(.2,.55,.35,1)'}));
  });

  const content = panel.querySelectorAll('.panel-meta, .large-step, #step-title, #step-description, .gate, .panel-bottom');
  content.forEach((element, order) => {
    const isNumber = element.classList.contains('large-step');
    stepAnimations.push(element.animate([
      {opacity: 0, transform: `translateY(${direction * (isNumber ? -14 : 10)}px)`},
      {opacity: 1, transform: 'translateY(0)'}
    ], {
      duration: isNumber ? 440 : 340,
      delay: order * 28,
      easing: 'cubic-bezier(.22,1,.36,1)',
      fill: 'backwards'
    }));
  });
});
function initFilePreview() {
  const workspace = document.querySelector('.workspace-preview');
  const panel = document.getElementById('file-panel');
  const preview = document.getElementById('file-preview');
  const toggle = document.getElementById('preview-toggle');
  const buttons = [...workspace.querySelectorAll('[data-file]')];
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const code = document.createElement('code');
  const written = document.createElement('span');
  const accessible = document.createElement('span');
  written.className = 'preview-written';
  written.setAttribute('aria-hidden', 'true');
  accessible.className = 'preview-accessible';
  code.append(written, accessible);
  preview.replaceChildren(code);
  buttons.forEach(button => {
    const progress = document.createElement('span');
    progress.className = 'file-progress';
    progress.setAttribute('aria-hidden', 'true');
    button.append(progress);
  });

  let current = 0;
  let inView = false;
  let autoplay = !motion.matches;
  let frame = 0;
  let nextTimer = 0;
  let progressAnimation;
  const holdTime = 2600;
  const characterTime = 18;

  function updateControl() {
    toggle.hidden = motion.matches;
    toggle.setAttribute('aria-label', `${autoplay ? 'Pause' : 'Play'} file preview animation`);
    toggle.querySelector('.preview-toggle-label').textContent = autoplay ? 'Pause' : 'Play';
    toggle.querySelector('.preview-toggle-icon').textContent = autoplay ? 'Ⅱ' : '▷';
  }
  function stop() {
    cancelAnimationFrame(frame);
    clearTimeout(nextTimer);
    progressAnimation?.cancel();
    workspace.dataset.playing = 'false';
    preview.dataset.typing = 'false';
  }
  function render(index, animateText = true) {
    stop();
    current = index;
    const [caption, text] = samples[index];
    document.getElementById('file-caption').textContent = caption;
    panel.setAttribute('aria-labelledby', buttons[index].id);
    accessible.textContent = text;
    updateControl();
    const canAnimate = inView && !document.hidden && !motion.matches;
    written.textContent = canAnimate && animateText ? '' : text;
    if (!canAnimate) return;

    workspace.dataset.playing = String(autoplay);
    const typingTime = animateText ? text.length * characterTime : 0;
    if (autoplay) {
      progressAnimation = buttons[index].querySelector('.file-progress').animate(
        [{transform: 'scaleX(0)'}, {transform: 'scaleX(1)'}],
        {duration: typingTime + holdTime, easing: 'linear', fill: 'forwards'}
      );
    }
    function finish() {
      preview.dataset.typing = 'false';
      if (autoplay) nextTimer = setTimeout(() => selectFile((current + 1) % samples.length, false, true), holdTime);
    }
    if (!typingTime) { finish(); return; }
    preview.dataset.typing = 'true';
    const started = performance.now();
    let lastCount = -1;
    function type(now) {
      const count = Math.min(text.length, Math.floor((now - started) / characterTime));
      if (count !== lastCount) { written.textContent = text.slice(0, count); lastCount = count; }
      if (count < text.length) frame = requestAnimationFrame(type);
      else finish();
    }
    frame = requestAnimationFrame(type);
  }
  const selectFile = tabs('[data-file]', (button, index, automatic) => {
    if (!automatic) autoplay = false;
    render(index);
  });
  toggle.addEventListener('click', () => {
    autoplay = !autoplay;
    render(current, autoplay);
  });
  workspace.addEventListener('focusin', event => {
    if (toggle.contains(event.target)) return;
    autoplay = false;
    render(current, false);
  });
  function resumeIfVisible() { render(current, autoplay); }
  document.addEventListener('visibilitychange', resumeIfVisible);
  motion.addEventListener('change', () => {
    autoplay = !motion.matches;
    resumeIfVisible();
  });
  new IntersectionObserver(entries => {
    const visible = entries[0].isIntersecting;
    if (visible === inView) return;
    inView = visible;
    resumeIfVisible();
  }, {threshold: 0.2}).observe(workspace);
  render(0, false);
}
initFilePreview();
function initInstallTabs() {
  const methods = {
    git: ['git clone https://github.com/lucasbabur/jp-essay ~/.claude/skills/jp-essay &&\n~/.claude/skills/jp-essay/install.sh', 'Installs the current general and scientific skills. Start a new Claude Code session after installation.'],
    npm: ['npm install -g jp-essay\njp-essay', 'npm currently publishes v0.1.0 with the earlier method. Choose Git for the nine-step process and scientific edition described here.'],
    npx: ['npx jp-essay@latest', 'The latest npm release is currently v0.1.0 with the earlier method. Choose Git for the current general and scientific skills.']
  };
  const panel = document.getElementById('install-panel');
  const command = document.getElementById('install-command');
  const status = document.getElementById('install-status');
  const statusSlot = document.createElement('div');
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  statusSlot.className = 'install-status-slot';
  status.before(statusSlot);
  statusSlot.append(status);

  // Overlaid, inaccessible sizing copies reserve the largest option at any width.
  // This also adapts automatically when fonts load or text wraps on mobile.
  for (const values of Object.values(methods)) {
    [command, status].forEach((element, index) => {
      const sizingCopy = element.cloneNode(false);
      sizingCopy.removeAttribute('id');
      sizingCopy.removeAttribute('role');
      sizingCopy.setAttribute('aria-hidden', 'true');
      sizingCopy.classList.add('install-size-ghost');
      sizingCopy.textContent = values[index];
      element.parentElement.append(sizingCopy);
    });
  }

  function stopAnimations() {
    [command, status].forEach(element => element.getAnimations().forEach(animation => animation.cancel()));
  }
  tabs('[data-install]', button => {
    stopAnimations();
    const values = methods[button.dataset.install];
    command.textContent = values[0];
    status.textContent = values[1];
    panel.setAttribute('aria-labelledby', button.id);
    if (motion.matches || !command.animate) return;
    [command, status].forEach(element => element.animate(
      [{opacity: 0, transform: 'translateY(3px)'}, {opacity: 1, transform: 'translateY(0)'}],
      {duration: 200, easing: 'ease-out'}
    ));
  });
  motion.addEventListener('change', () => {
    if (motion.matches) stopAnimations();
  });
}
initInstallTabs();
let toastTimer;
function notify(message) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('visible'), 3500);
}
async function copy(id) {
  const value = document.getElementById(id).textContent;
  try {
    if (!navigator.clipboard) throw new Error('Clipboard unavailable');
    await navigator.clipboard.writeText(value);
    notify('Command copied.');
  } catch {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(document.getElementById(id));
    selection.removeAllRanges(); selection.addRange(range);
    notify('Command selected. Press Ctrl+C or ⌘C to copy.');
  }
}
document.getElementById('copy-hero-install').addEventListener('click', () => copy('hero-install-command'));
document.getElementById('copy-install').addEventListener('click', () => copy('install-command'));
document.getElementById('copy-usage').addEventListener('click', () => copy('usage-command'));

// Prefer the local cached endpoint; static hosting falls back to GitHub's public API.
async function refreshGitHubStars() {
  const count = document.getElementById('github-star-count');
  if (!count) return;
  for (const url of ['https://api.github.com/repos/lucasbabur/jp-essay']) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 8000);
    try {
      const response = await fetch(url, {
        headers: {Accept: 'application/json'},
        cache: 'no-store',
        signal: controller.signal
      });
      if (!response.ok) continue;
      const repository = await response.json();
      const stars = repository.stargazers_count;
      if (!Number.isSafeInteger(stars) || stars < 0) continue;
      const total = stars.toLocaleString('en');
      count.textContent = total;
      count.parentElement.setAttribute('aria-label', `${total} ${stars === 1 ? 'star' : 'stars'} on GitHub`);
      count.parentElement.title = `${total} ${stars === 1 ? 'star' : 'stars'} on GitHub`;
      return;
    } catch {
      // Keep the last verified count if both sources are unavailable.
    } finally {
      clearTimeout(timer);
    }
  }
  if (count.textContent === '—') {
    count.parentElement.setAttribute('aria-label', 'GitHub star count unavailable');
    count.parentElement.title = 'View the current star count on GitHub';
  }
}
refreshGitHubStars();
document.addEventListener('visibilitychange', () => {
  if (!document.hidden) refreshGitHubStars();
});
setInterval(() => {
  if (!document.hidden) refreshGitHubStars();
}, 60000);


// Keep native details semantics while animating both directions.
function animateFaq() {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  document.querySelectorAll('.faq details').forEach(details => {
    const summary = details.querySelector('summary');
    const answer = details.querySelector('p');
    let expanded = details.open;
    let heightAnimation;
    let answerAnimation;
    const overflow = details.style.overflow;
    summary.setAttribute('aria-expanded', String(expanded));

    function finish() {
      details.open = expanded;
      heightAnimation?.cancel();
      answerAnimation?.cancel();
      heightAnimation = answerAnimation = null;
      details.style.overflow = overflow;
    }

    summary.addEventListener('click', event => {
      event.preventDefault();
      const startHeight = details.getBoundingClientRect().height;
      const startOpacity = details.open ? getComputedStyle(answer).opacity : '0';
      heightAnimation?.cancel();
      answerAnimation?.cancel();
      expanded = !expanded;
      summary.setAttribute('aria-expanded', String(expanded));
      details.open = expanded;
      if (reducedMotion.matches || !details.animate) {
        finish();
        return;
      }

      const endHeight = details.getBoundingClientRect().height;
      details.open = true;
      details.style.overflow = 'hidden';
      heightAnimation = details.animate(
        [{height: `${startHeight}px`}, {height: `${endHeight}px`}],
        {duration: 280, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'both'}
      );
      answerAnimation = answer.animate(
        [{opacity: startOpacity}, {opacity: expanded ? 1 : 0}],
        {duration: 200, easing: 'ease-out', fill: 'both'}
      );
      heightAnimation.onfinish = finish;
    });
    reducedMotion.addEventListener('change', () => {
      if (reducedMotion.matches) finish();
    });
  });
}
animateFaq();
