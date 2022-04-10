{
  let formData = {};
  let pipeline_data = {};

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

    let agentElement = document.getElementsByName("agent");
    record_input_data(agentElement, "agent");

    let stageElement = document.getElementsByName("stage");
    record_input_data(stageElement, "stage");

    let whenElement = document.getElementsByName("when");
    record_input_data(whenElement, "when_child");

    let shElement = document.getElementsByName("sh");
    record_input_data(shElement, "sh");

    let alwaysShElement = document.getElementsByName("always_sh");
    record_input_data(alwaysShElement, "always_sh");

    let echoElement = document.getElementsByName("echo");
    record_input_data(echoElement, "echo");

    let alwaysEchoElement = document.getElementsByName("always_echo");
    record_input_data(alwaysEchoElement, "always_echo");

    let junitElement = document.getElementsByName("junit");
    record_input_data(junitElement, "junit");

    let jacocoElement = document.getElementsByName("jacoco");
    record_input_data(jacocoElement, "jacoco");
  }


  /**
   * 將 class="pipeline" 的 DOM 轉成 json, 並加上 form 的值
   */
  function combinePipeline() {
    let jenkins_file = document.querySelector(".pipeline");
    getFormValue()
    pipeline_data = showStringifyResult(jenkins_file)
  }


  /**
   * DOM to Json
   * @param target 需轉成 Json 形式的 DOM
   * @returns {string} Json 形式的字串
   */
  function showStringifyResult(target) {
    return JSON.stringify(stringify(target), null, "");
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


  /* 使用 ajax 將 pipeline 資料 (json 格式) 傳遞至後端 */
  let btn = document.querySelector(".btn_pipe");
  btn.onclick = function() {
    // 抓取頁面元素，準備 json 資料(使 pipeline_data 可用)
    combinePipeline();
    // jquery ajax
    let code_sector = document.querySelector(".pipeline_content");
    const pipeparser_url = "/flow/pipeparser/";
    $.ajax({
      type: "POST",
      url: pipeparser_url,
      contentType: "application/json",
      data: pipeline_data,
      datatype: "text/plain",
      success: function (response) {
        code_sector.innerHTML = response;
      },
      error: function (response) {
        code_sector.innerHTML = "Oops! Something error when parse jenkinsfile."
      }
    });
  };
}

{
  let btnDownload = document.querySelector('#btn_download')
  btnDownload.onclick = function () {
    let aTag = document.createElement('a');
    let pipelineText = document.querySelector('.pipeline_content').innerHTML;
    let blob = new Blob([pipelineText], {
      type: "application/octet-stream",
    })
    aTag.download = 'Jenkinsfile';
    aTag.href = URL.createObjectURL(blob);
    aTag.click();
    URL.revokeObjectURL(aTag.href);
  }
}
