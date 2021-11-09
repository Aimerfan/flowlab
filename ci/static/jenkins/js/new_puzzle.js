function newAgent() {
  let layer = 2;
  let idAgent = 1;

  document.getElementById("addAgent").style.display = "none";
  let block = document.getElementById("agent");
  block.className += " agent"
  block.id = "agent_" + idAgent;

  let agentLabel = document.createElement("label");
  agentLabel.for = "agent";
  let agentInput = document.createElement("input");
  agentInput.type = "text";
  agentInput.id  = "agent_" + idAgent;
  agentInput.className = "form-control puz_form";
  agentInput.name = "agent";
  agentLabel.appendChild(agentInput)
  let agent = document.createElement("div");
  agent.className = "jenkins_puzzle puz_" + layer;
  agent.append("agent ", agentLabel)

  block.appendChild(agent);
}

function newStages() {
  let layer = 2;
  document.getElementById("addStages").style.display = "none";
  let block = document.getElementById("stages");
  block.className += " stages"

  let stages = document.createElement("div");
  stages.textContent = "stages";
  stages.className = "jenkins_puzzle puz_" + layer;

  let choiceStage = document.createElement("div");
  choiceStage.className = "jenkins_puzzle puz_add puz_" + (layer + 1);
  choiceStage.textContent = "+ stage";
  choiceStage.id = "addStage"
  choiceStage.addEventListener("click", newStage.bind(this, (layer + 1), "stages", true));

  block.append(stages, choiceStage);
}


{
  let idStage = 0;
  let idWhen = 0;
  let idSteps = 0;
  let idParallel = 0;

  /**
   * 新增 Stage 區段
   * @param {number} layer 指定 css 的 class 樣式為第幾階層
   * @param {String} parentId 被新增的父區塊 id
   * @param {boolean} allowParallel 能否生成 "+ parallel" 區塊
   */
  function newStage(layer, parentId, allowParallel) {
    let stages = document.getElementById(parentId);

    let block = document.createElement("div");
    block.className = "puz_bl_" + layer + " stage";
    idStage += 1;
    block.id = "stage_" + idStage;
    stages.appendChild(block);

    let stageLabel = document.createElement("label");
    stageLabel.for = "stage_" + idStage;
    let stageInput = document.createElement("input");
    stageInput.type = "text";
    stageInput.id  = "stage_" + idStage;
    stageInput.className = "form-control puz_form";
    stageInput.name = "stage";
    stageLabel.appendChild(stageInput)
    let stage = document.createElement("div");
    stage.className = "jenkins_puzzle puz_" + layer;
    stage.append("stage(", stageLabel, ")")

    let choiceWhen = document.createElement("div");
    choiceWhen.className = "jenkins_puzzle puz_add puz_" + (layer + 1);
    choiceWhen.textContent = "+ when";
    idWhen += 1;
    choiceWhen.id = "addWhen_" + idWhen;
    choiceWhen.addEventListener("click", newWhen.bind(this, (layer + 1), idStage, idWhen));

    let choiceSteps = document.createElement("div");
    choiceSteps.className = "jenkins_puzzle puz_add puz_" + (layer + 1);
    choiceSteps.textContent = "+ steps";
    idSteps += 1;
    choiceSteps.id = "addSteps_" + idSteps;
    choiceSteps.addEventListener("click", newSteps.bind(this, (layer + 1), idStage, idSteps));

    if (allowParallel) {
      let choiceParallel = document.createElement("div");
      choiceParallel.className = "jenkins_puzzle puz_add puz_" + (layer + 1);
      choiceParallel.textContent = "+ parallel";
      idParallel += 1;
      choiceParallel.id = "addParallel_" + idParallel;
      choiceParallel.addEventListener("click", newParallel.bind(this, (layer + 1), idStage, idParallel));

      block.append(stage, choiceWhen, choiceSteps, choiceParallel);
    } else {
      block.append(stage, choiceWhen, choiceSteps);
    }
  }
}


function newWhen(layer, idStage, idWhen) {
  document.getElementById("addWhen_" + idWhen).style.display = "none";
  let stage = document.getElementById("stage_" + idStage);

  let block = document.createElement("div");
  block.className = "puz_bl_" + layer + " when";
  block.id = "when_" + idWhen;

  let steps = document.getElementById("steps_" + idStage);
  let parallel = document.getElementById("parallel_" + idStage);
  // 若已有 "steps" 區塊, 則在該 "steps" 區塊前 加入 "when" 區塊
  if (steps) {
    stage.insertBefore(block, steps);
  }
  // 若已有 "parallel" 區塊, 則在該 "parallel" 區塊前 加入 "when" 區塊
  else if (parallel) {
    stage.insertBefore(block, parallel);
  } else {
    stage.appendChild(block);
  }

  let whenChildLabel = document.createElement("label");
  whenChildLabel.for = "when_child_" + idWhen;
  let whenChildInput = document.createElement("textarea");
  whenChildInput.type = "text";
  whenChildInput.id  = "when_child_" + idWhen;
  whenChildInput.className = "form-control puz_form width_textarea";
  whenChildInput.name = "when";
  whenChildLabel.appendChild(whenChildInput)

  let when = document.createElement("div");
  when.className = "ver_top jenkins_puzzle puz_" + layer;
  when.textContent = "when";

  when.appendChild(whenChildLabel);
  block.append(when);
}


function newSteps(layer, idStage, idSteps) {
  document.getElementById("addSteps_" + idSteps).style.display = "none";
  // FIXME: 僅與 "parallel" 同階層時, 新增 steps, 才需隱藏 "+ parallel"
  // document.getElementById("addParallel_" + idSteps).style.display = "none";
  let stage = document.getElementById("stage_" + idStage);

  let block = document.createElement("div");
  block.className = "puz_bl_" + layer + " steps";
  block.id = "steps_" + idSteps;
  stage.appendChild(block);

  let steps = document.createElement("div");
  steps.className = "jenkins_puzzle puz_" + layer;
  steps.textContent = "steps";

  let choiceSh = document.createElement("div");
  choiceSh.className = "jenkins_puzzle puz_add puz_" + (layer + 1);
  choiceSh.textContent = "+ sh";
  choiceSh.id = "addSh_" + idSteps;
  choiceSh.addEventListener("click", newSh.bind(this, (layer + 1), idSteps));

  let choiceEcho = document.createElement("div");
  choiceEcho.className = "jenkins_puzzle puz_add puz_" + (layer + 1);
  choiceEcho.textContent = "+ echo";
  choiceEcho.id = "addEcho_" + idSteps;
  choiceEcho.addEventListener("click", newEcho.bind(this, (layer + 1), idSteps));

  block.append(steps, choiceSh, choiceEcho);
}


function newParallel(layer, idStage, idParallel) {
  document.getElementById("addSteps_" + idStage).style.display = "none";
  document.getElementById("addParallel_" + idParallel).style.display = "none";
  let stage = document.getElementById("stage_" + idStage);

  let block = document.createElement("div");
  block.className = "puz_bl_" + layer + " parallel";
  block.id = "parallel_" + idParallel;
  stage.appendChild(block);

  let parallel = document.createElement("div");
  parallel.className = "jenkins_puzzle puz_" + layer;
  parallel.textContent = "parallel";

  let choiceStage = document.createElement("div");
  choiceStage.className = "jenkins_puzzle puz_add puz_" + (layer + 1);
  choiceStage.textContent = "+ stage"
  choiceStage.id = "addStage"
  choiceStage.addEventListener("click", newStage.bind(this, (layer + 1), block.id, false));

  block.append(parallel, choiceStage);
}


{
  let idSh = 0;

  function newSh(layer, idSteps) {
    let steps = document.getElementById("steps_" + idSteps);

    let block = document.createElement("div");
    block.className = "puz_bl_" + layer + " sh";
    idSh += 1;
    block.id = "sh_" + idSh;
    steps.appendChild(block);

    let shLabel = document.createElement("label");
    shLabel.for = "sh_" + idSh;
    let shTextarea = document.createElement("textarea");
    shTextarea.id = "sh_" + idSh;
    shTextarea.className = "form-control puz_form width_textarea";
    shTextarea.name = "sh";
    shLabel.appendChild(shTextarea)
    let sh = document.createElement("div");
    sh.className = "ver_top jenkins_puzzle puz_" + layer;
    sh.append("sh", shLabel)

    block.appendChild(sh);
  }
}


{
  let idEcho = 0;

  function newEcho(layer, idSteps) {
    let steps = document.getElementById("steps_" + idSteps);

    let block = document.createElement("div");
    block.className = "puz_bl_" + layer + " echo";
    idEcho += 1;
    block.id = "echo_" + idSteps + "_" + idEcho;
    steps.appendChild(block)

    let echoLabel = document.createElement("label");
    echoLabel.for = "echo_" + idEcho;
    let echoInput = document.createElement("input");
    echoInput.type = "text";
    echoInput.id = "echo_" + idEcho;
    echoInput.className = "form-control puz_form";
    echoInput.name = "echo";
    echoLabel.appendChild(echoInput)
    let sh = document.createElement("div");
    sh.className = "jenkins_puzzle puz_" + layer;
    sh.append("echo", echoLabel)

    block.appendChild(sh);
  }
}
