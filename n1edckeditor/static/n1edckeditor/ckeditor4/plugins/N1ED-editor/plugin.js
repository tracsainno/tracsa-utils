/*!
 * Add-on for including N1ED into your CKEditor 4
 * Developer: N1ED
 * Website: https://n1ed.com/
 * License: GPL v3
 */


/*
 *   HOW TO INSTALL THIS ADD-ON
 *
 *   1. Copy the plugin into
 *
 *        ckeditor/
 *          plugins/
 *            N1ED-editor/
 *              plugin.js
 *
 *   2. Add "N1ED-editor" to the "extraPlugins" config option
 *   3. Done
 *
 *
 *   VISUAL CONFIGURATION
 *
 *   Configure N1ED visually using the Dashboard:
 *
 *       https://n1ed.com/dashboard
 *
 *   Get an API key there and link it to your installation.
 *   Specify it as a CKEditor parameter:
 *
 *       apiKey: "..."
 */

(function() {

    var PLUGIN_NAME = "N1ED-editor";
    var DEFAULT_API_KEY = "N1ED24RR1234123412341234";

    window.n1edPluginVersion=202609001;
    window.n1edPluginEditor="ckeditor";

    function get(varName, defaultValue) {
        if (window[varName] !== undefined && window[varName] !== "-")
            return window[varName];
        else
            return defaultValue;
    }

    window.CKEDITOR_OVERRIDE_API_KEY_PARAM = "OVERRIDE_API_KEY";

    function resolveApiKey() {
        if (window.OVERRIDE_API_KEY)
            return window.OVERRIDE_API_KEY;
        if (window.N1ED_API_KEY)
            return window.N1ED_API_KEY;
        if (CKEDITOR.config.apiKey)
            return CKEDITOR.config.apiKey;
        var ids = Object.keys(CKEDITOR.instances);
        for (var i = 0; i < ids.length; i++) {
            var config = CKEDITOR.instances[ids[i]].config;
            if (config.apiKey)
                return config.apiKey;
            if (config.Flmngr && config.Flmngr.apiKey)
                return config.Flmngr.apiKey;
        }
        return null;
    }

    var apiKey = null;

    var version = get("N1ED_VERSION", "latest");
    var n1edPrefix = get("N1ED_PREFIX", null);
    if (n1edPrefix !== null && n1edPrefix !== "local")
        n1edPrefix = null;
    var n1edHttps = get("N1ED_HTTPS", true);

    var protocol = n1edHttps ? "https" : "http";

    var host = (n1edPrefix ? (n1edPrefix + ".") : "") + "cloud.n1ed.com";

    function buildPluginUrl(key) {
        return protocol + "://" + host + "/a/" + key + "/plugins/N1EDEco/plugin.js";
    }

    function getOurPluginName(url) {
        var mHost = ("" + url).match(/^https?:\/\/([^\/]+)/);
        if (!mHost || (mHost[1] !== host && mHost[1] !== "cloud.n1ed.com"))
            return null;
        var mName = ("" + url).match(/\/plugins\/([^\/]+)\/plugin\.js/);
        return mName ? mName[1] : null;
    }

    function stubPlugin(pluginName) {
        if (!(pluginName in CKEDITOR.plugins.registered)) {
            console.log("Using a stub for '" + pluginName + "' plugin, the editor starts without it");
            CKEDITOR.plugins.add(pluginName, {"n1edStub": 1});
            if (pluginName === "N1EDEco")
                window.n1edEcoUnavailable = new Date().getTime();
        }
    }

    if (window.n1edFailsafe !== 2) {
        window.n1edFailsafe = 2;

        var oldScriptLoaderLoad = window.CKEDITOR.scriptLoader.load;
        window.CKEDITOR.scriptLoader.load = function(scriptUrl, callback, scope, showBusy) {

            if (typeof scriptUrl === "string" || typeof callback !== "function")
                return oldScriptLoaderLoad.call(this, scriptUrl, callback, scope, showBusy);

            var ourUrls = [];
            var otherUrls = [];
            var onlyEco = true;
            for (var i = 0; i < scriptUrl.length; i++) {
                var name = getOurPluginName(scriptUrl[i]);
                (name ? ourUrls : otherUrls).push(scriptUrl[i]);
                if (name && name !== "N1EDEco")
                    onlyEco = false;
            }

            if (ourUrls.length === 0)
                return oldScriptLoaderLoad.call(this, scriptUrl, callback, scope, showBusy);

            var completedAll = [];
            var failedAll = [];
            var partsLeft = otherUrls.length > 0 ? 2 : 1;

            var onPartDone = function() {
                partsLeft--;
                if (partsLeft > 0)
                    return;

                var i;
                for (i = 0; i < completedAll.length; i++) {
                    var pluginName = getOurPluginName(completedAll[i]);
                    if (pluginName)
                        stubPlugin(pluginName);
                }

                var elsLoaders = document.querySelectorAll(".n1ed_loading");
                for (i = 0; i < elsLoaders.length; i++)
                    elsLoaders.item(i).parentElement.removeChild(elsLoaders.item(i));

                callback.apply(scope || CKEDITOR, [completedAll, failedAll]);
            };

            var handled = false;
            var timer = null;
            var onOurs = function(completed, failed) {
                if (handled)
                    return;
                handled = true;
                if (timer !== null)
                    clearTimeout(timer);
                var i;
                for (i = 0; i < (completed || []).length; i++)
                    completedAll.push(completed[i]);
                for (i = 0; i < (failed || []).length; i++) {
                    console.error("Cannot load " + failed[i]);
                    completedAll.push(failed[i]);
                }
                onPartDone();
            };

            var timeoutMs = typeof window.N1ED_FAILSAFE_TIMEOUT === "number" ? window.N1ED_FAILSAFE_TIMEOUT : 7000;
            if (!onlyEco)
                timeoutMs = timeoutMs * 2;
            if (timeoutMs > 0) {
                timer = setTimeout(function() {
                    console.warn("Could not reach our server in " + timeoutMs + " ms (network issue?), starting the editor without cloud plugins");
                    onOurs(ourUrls.slice(), []);
                }, timeoutMs);
            }
            oldScriptLoaderLoad.call(this, ourUrls, onOurs, scope, false);

            if (otherUrls.length > 0)
                oldScriptLoaderLoad.call(this, otherUrls, function(completed, failed) {
                    var i;
                    for (i = 0; i < (completed || []).length; i++)
                        completedAll.push(completed[i]);
                    for (i = 0; i < (failed || []).length; i++)
                        failedAll.push(failed[i]);
                    onPartDone();
                }, scope, showBusy);
        };
    }

    function addEcoExternal(key) {
        if (!("N1EDEco" in CKEDITOR.plugins.externals))
            CKEDITOR.plugins.addExternal("N1EDEco", buildPluginUrl(key));
    }

    apiKey = resolveApiKey();

    if (!apiKey && Object.keys(CKEDITOR.instances).length === 0) {

        if (!(PLUGIN_NAME in CKEDITOR.plugins.registered))
            CKEDITOR.plugins.add(PLUGIN_NAME, {});

        CKEDITOR.once("instanceCreated", function(e) {
            e.editor.on("configLoaded", function() {
                apiKey = resolveApiKey();
                if (!apiKey) {
                    apiKey = DEFAULT_API_KEY;
                    console.warn("No API key found in the editor config, using our demo key - set config.apiKey to use your own");
                }
                addEcoExternal(apiKey);
                CKEDITOR.plugins.registered[PLUGIN_NAME].requires = ["N1EDEco"];
            });
        });

    } else {

        if (!apiKey) {
            apiKey = DEFAULT_API_KEY;
        }
        addEcoExternal(apiKey);
        if (!(PLUGIN_NAME in CKEDITOR.plugins.registered))
            CKEDITOR.plugins.add( PLUGIN_NAME, {
                "requires": ["N1EDEco"]
            });

    }

    function applyPatch() {
        window.applyPatch && window.applyPatch(PLUGIN_NAME, window.n1edPluginVersion, apiKey || DEFAULT_API_KEY);
    }
    var script = document.createElement('script');
    script.type = "text/javascript";
    script.src = protocol + "://" + host + "/static/pluginPatch.js";
    document.head.appendChild(script);
    if (script.readyState) {
        script.onreadystatechange = function () {
            if (script.readyState === "loaded" || script.readyState === "complete") {
                script.onreadystatechange = null;
                applyPatch();
            }
        };
    } else {
        script.onload = function () {
            applyPatch();
        };
    }

})()