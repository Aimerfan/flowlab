{
  let formData = {};

  /**
   * 取表單中的值
   * 以 formData = { id: value, ... } 的格式儲存
   */
  function getFormValue() {

    function record_input_data(element, keyword) {
      for (let i = 0; i < element.length; i++) {
        let index = keyword + "_" + (i + 1);
        formData[index] = element[i].value;
      }
    }

    let stageElement = document.getElementsByName("stage");
    record_input_data(stageElement, "stage");

    let singleShElement = document.getElementsByName("single_sh");
    record_input_data(singleShElement, "single_sh");

    let multiShElement = document.getElementsByName("multi_sh");
    record_input_data(multiShElement, "multi_sh");

    let echoElement = document.getElementsByName("echo");
    record_input_data(echoElement, "echo");
  }


  function getJenkinsFile() {

    getFormValue()

    // 以隱藏的表單送資料至後端
    let jenkins_file = document.querySelector(".pipeline");
    let block = document.getElementById("pipe_form");
    // 傳遞 html 區塊 (json 格式)
    let input_frame = document.createElement("input");
    input_frame.value = showStringifyResult(jenkins_file);
    input_frame.name = "context";
    input_frame.type = "hidden";
    // 傳遞 form 資料 (json 格式)
    let input_value = document.createElement("input");
    input_value.value = JSON.stringify(formData);
    input_value.name = "data";
    input_value.type = "hidden";
    block.append(input_frame, input_value);

    document.forms["pipe_form"].submit();
  }


  /**
   * DOM to Json
   * @param target 需轉成 Json 形式的 DOM
   * @returns {string} Json 形式的字串
   */
  function showStringifyResult(target) {
    return JSON.stringify(stringify(target), null, ' ');
  }


  /**
   * 將 DOM 重新整理, 並加入 form 的 values
   * @param element html 元素
   * @returns {{}} 整理過後的 DOM
   */
  function stringify(element) {
    let obj = {};
    obj.name = element.localName;
    obj.attributes = [];
    obj.children = [];
    let valueExist = 0;
    Array.from(element.attributes).forEach(a => {
      // 若為 input/textarea tag 且尚無 value 時, 增加 value 屬性
      if ((obj.name === "input" || obj.name === "textarea") && !valueExist) {
        // 由 input.id 找相對應的 input.value
        if (a.name === "id") {
          let value = formData[a.value];
          obj.attributes.push({name: "value", value: value});
          valueExist = 1;
        }
      }
      obj.attributes.push({ name: a.name, value: a.value });
    });
    Array.from(element.children).forEach(c => {
      obj.children.push(stringify(c));
    });

    return obj;
  }


  /* 使用 ajax 將 pipeline 資料 (json 格式) 顯示於網頁上 */
  let xhr = new XMLHttpRequest();
  xhr.open("get","",true);
  xhr.send(null);
  xhr.onload = function(){
    let info = document.querySelector(".info");
    let btn = document.querySelector(".btn_pipe");
    btn.onclick = function(e){
      let jenkins_file = document.querySelector(".pipeline");
      getFormValue()
      info.innerHTML += showStringifyResult(jenkins_file);
    };
  };
}


function newStages() {
  let layer = 2;
  document.getElementById("addStages").style.display = "none";
  let block = document.getElementById("stages");

  let stages = document.createElement("div");
  stages.textContent = "stages";
  stages.className = "stages jenkins_puzzle puz_" + layer;

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
    block.className = "puz_bl_" + layer;
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
    stage.className = "stage jenkins_puzzle puz_" + layer;
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
  block.className = "puz_bl_" + layer;
  block.id = "when_" + idWhen;

  let steps = document.getElementById("steps_" + idStage);
  let parallel = document.getElementById("parallel_" + idStage);
  // 若已有 "steps" 區塊, 則在該 "steps" 區塊前 加入 "when" 區塊
  if (steps) {
    stage.insertBefore(block, steps)
  }
  // 若已有 "parallel" 區塊, 則在該 "parallel" 區塊前 加入 "when" 區塊
  else if (parallel) {
    stage.insertBefore(block, parallel)
  } else {
    stage.appendChild(block);
  }

  let when = document.createElement("div");
  when.className = "when jenkins_puzzle puz_" + layer;
  when.textContent = "when";

  block.appendChild(when);
}


function newSteps(layer, idStage, idSteps) {
  document.getElementById("addSteps_" + idSteps).style.display = "none";
  // FIXME: 僅與 "parallel" 同階層時, 新增 steps, 才需隱藏 "+ parallel"
  // document.getElementById("addParallel_" + idSteps).style.display = "none";
  let stage = document.getElementById("stage_" + idStage);

  let block = document.createElement("div");
  block.className = "puz_bl_" + layer;
  block.id = "steps_" + idSteps;
  stage.appendChild(block);

  let steps = document.createElement("div");
  steps.className = "steps jenkins_puzzle puz_" + layer;
  steps.textContent = "steps";

  let choiceSingleSh = document.createElement("div");
  choiceSingleSh.className = "jenkins_puzzle puz_add puz_" + (layer + 1);
  choiceSingleSh.textContent = "+ sh (single row)";
  choiceSingleSh.id = "addSingleSh_" + idSteps;
  choiceSingleSh.addEventListener("click", newSingleSh.bind(this, (layer + 1), idSteps));

  let choiceMultiSh = document.createElement("div");
  choiceMultiSh.className = "jenkins_puzzle puz_add puz_" + (layer + 1);
  choiceMultiSh.textContent = "+ sh (multi row)";
  choiceMultiSh.id = "addMultiSh_" + idSteps;
  choiceMultiSh.addEventListener("click", newMultiSh.bind(this, (layer + 1), idSteps));

  let choiceEcho = document.createElement("div");
  choiceEcho.className = "jenkins_puzzle puz_add puz_" + (layer + 1);
  choiceEcho.textContent = "+ echo";
  choiceEcho.id = "addEcho_" + idSteps;
  choiceEcho.addEventListener("click", newEcho.bind(this, (layer + 1), idSteps));

  block.append(steps, choiceSingleSh, choiceMultiSh, choiceEcho);
}


function newParallel(layer, idStage, idParallel) {
  document.getElementById("addSteps_" + idStage).style.display = "none";
  document.getElementById("addParallel_" + idParallel).style.display = "none";
  let stage = document.getElementById("stage_" + idStage);

  let block = document.createElement("div");
  block.className = "puz_bl_" + layer;
  block.id = "parallel_" + idParallel;
  stage.appendChild(block);

  let parallel = document.createElement("div");
  parallel.className = "parallel jenkins_puzzle puz_" + layer;
  parallel.textContent = "parallel";

  let choiceStage = document.createElement("div");
  choiceStage.className = "jenkins_puzzle puz_add puz_" + (layer + 1);
  choiceStage.textContent = "+ stage"
  choiceStage.id = "addStage"
  choiceStage.addEventListener("click", newStage.bind(this, (layer + 1), block.id, false));

  block.append(parallel, choiceStage);
}


{
  let idSingleSh = 0;

  function newSingleSh(layer, idSteps) {
    let steps = document.getElementById("steps_" + idSteps);

    let block = document.createElement("div");
    block.className = "puz_bl_" + layer;
    idSingleSh += 1;
    block.id = "single_sh_" + idSteps + "_" + idSingleSh;
    steps.appendChild(block);

    let shLabel = document.createElement("label");
    shLabel.for = "single_sh_" + idSingleSh;
    let shInput = document.createElement("input");
    shInput.type = "text";
    shInput.id = "single_sh_" + idSingleSh;
    shInput.className = "form-control puz_form";
    shInput.name = "single_sh";
    shLabel.appendChild(shInput)
    let singleSh = document.createElement("div");
    singleSh.className = "single_sh jenkins_puzzle puz_" + layer;
    singleSh.append("sh", shLabel)

    block.appendChild(singleSh);
  }
}


{
  let idMultiSh = 0;

  function newMultiSh(layer, idSteps) {
    let steps = document.getElementById("steps_" + idSteps);

    let block = document.createElement("div");
    block.className = "puz_bl_" + layer;
    idMultiSh += 1;
    block.id = "multi_sh_" + idSteps + "_" + idMultiSh;
    steps.appendChild(block);

    let shLabel = document.createElement("label");
    shLabel.for = "multi_sh_" + idMultiSh;
    let shTextarea = document.createElement("textarea");
    shTextarea.id = "multi_sh_" + idMultiSh;
    shTextarea.className = "form-control puz_form";
    shTextarea.name = "multi_sh";
    shLabel.appendChild(shTextarea)
    let multiSh = document.createElement("div");
    multiSh.className = "multi_sh jenkins_puzzle puz_" + layer;
    multiSh.append("sh", shLabel)

    block.appendChild(multiSh);
  }
}


{
  let idEcho = 0;

  function newEcho(layer, idSteps) {
    let steps = document.getElementById("steps_" + idSteps);

    let block = document.createElement("div");
    block.className = "puz_bl_" + layer;
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
    let multiSh = document.createElement("div");
    multiSh.className = "echo jenkins_puzzle puz_" + layer;
    multiSh.append("echo", echoLabel)

    block.appendChild(multiSh);
  }
}
