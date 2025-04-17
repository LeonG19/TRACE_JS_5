<h1> Tools </h1>

<script>

    function gotoCrawler() {
      window.location.href = "/main/tools/Crawler";
    }
    function gotoFuzzer() {
      window.location.href = "/main/tools/Fuzzer";
    }

    function gotoBruteForcer() {
      window.location.href = "/main/tools/BruteForcer";
    }

    function gotoAI() {
      window.location.href = "/main/tools/AI";
    }

    function gotoHTTPTester() {
      window.location.href = "/main/tools/HTTPTester";
    }
    
    </script>
    
    <nav>
      <div class="toolsConfigPage">
        <div class="row">
          <span> Crawler </span>
          <button on:click={gotoCrawler} title="Navigates to the Crawler page">Select</button>
        </div>

        <div class="row">
          <span> Fuzzer </span>
          <button on:click={gotoFuzzer} title="Navigates to the Fuzzer page">Select</button>
        </div>

        <div class="row">
          <span> Brute Forcer </span>
          <button on:click={gotoBruteForcer}>Select</button>
        </div>

        <div class="row">
          <span> AI Credential Generator </span>
          <button on:click={gotoAI} title="Navigates to the AI Credential Generastor page">Select</button>
        </div>

        <div class="row">
          <span> HTTP Tester </span>
          <button on:click={gotoHTTPTester} title="Navigates to the HTTP Tester page">Select</button>
        </div>
        
      </div>
    </nav>