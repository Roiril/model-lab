// uHand の FBX を Unity で動かせる形に組む（Editor 専用）。
//
// 1. Assets/UHand/ に hiwonder-uhand-rigged.fbx と hiwonder-uhand-rigged.json を置くと、読み込み設定が自動で入る
//    （Generic、クリップ名の "uhand|" を外す、繰り返しの有無を目録から入れる）
// 2. メニュー Tools > uHand > Build Animator Controller で、次を作る
//      Assets/UHand/UHand.controller   層 0 がクリップの再生、その上にサーボ 1 個ぶんの層が 6 枚
//      Assets/UHand/Masks/*.mask        層ごとに動かす骨を絞るマスク
//      Assets/UHand/UHand.prefab        Animator と UHandDriver が付いたプレハブ
// 3. Tools > uHand > Verify は、クリップと量から出した姿勢を目録の目印（骨どうしの距離）と比べる
//
// クリップや形を作り直したら、model-lab 側で anim_build.py を回し、unity_install.py で入れ直してから 2 をやり直す。
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;

namespace UHand.EditorTools
{
    [Serializable]
    public class ManifestClip
    {
        public string name;
        public int frames;
        public float seconds;
        public bool loop;
        public string description;
    }

    [Serializable]
    public class ManifestDof
    {
        public string name;
        public float min;
        public float max;
        public float rest;
        public string[] bones;
        public string clip;
    }

    [Serializable]
    public class ManifestProbe
    {
        public string kind;
        public string clip;
        public float time;
        public float[] values;
        public string a;
        public string b;
        public float dist;
    }

    [Serializable]
    public class Manifest
    {
        public int fps;
        public string armature;
        public ManifestDof[] dof_list;
        public ManifestClip[] clips;
        public ManifestProbe[] probes;
    }

    public static class UHandPaths
    {
        public const string Dir = "Assets/UHand";
        public const string Fbx = Dir + "/hiwonder-uhand-rigged.fbx";
        public const string Json = Dir + "/hiwonder-uhand-rigged.json";
        public const string Controller = Dir + "/UHand.controller";
        public const string Prefab = Dir + "/UHand.prefab";
        public const string Masks = Dir + "/Masks";

        public static Manifest LoadManifest()
        {
            if (!File.Exists(Json)) throw new FileNotFoundException("目録が無い: " + Json);
            return JsonUtility.FromJson<Manifest>(File.ReadAllText(Json));
        }
    }

    // FBX の読み込み設定
    public class UHandPostprocessor : AssetPostprocessor
    {
        bool IsUHand => assetPath.Replace('\\', '/').EndsWith("/hiwonder-uhand-rigged.fbx");

        void OnPreprocessModel()
        {
            if (!IsUHand) return;
            var mi = (ModelImporter)assetImporter;
            mi.animationType = ModelImporterAnimationType.Generic;
            mi.importAnimation = true;
            mi.animationCompression = ModelImporterAnimationCompression.Off;   // 1 フレームごとに焼いてあるので間引かない
        }

        void OnPreprocessAnimation()
        {
            if (!IsUHand) return;
            var mi = (ModelImporter)assetImporter;
            var loops = new Dictionary<string, bool>();
            if (File.Exists(UHandPaths.Json))
                foreach (var c in UHandPaths.LoadManifest().clips) loops[c.name] = c.loop;
            var takes = mi.defaultClipAnimations;
            foreach (var t in takes)
            {
                int bar = t.name.LastIndexOf('|');          // Blender は "骨組みの名前|クリップ名" で出す
                if (bar >= 0) t.name = t.name.Substring(bar + 1);
                t.loopTime = loops.TryGetValue(t.name, out bool loop) && loop;
            }
            mi.clipAnimations = takes;
        }
    }

    public static class UHandSetup
    {
        static Dictionary<string, AnimationClip> LoadClips()
        {
            return AssetDatabase.LoadAllAssetsAtPath(UHandPaths.Fbx).OfType<AnimationClip>()
                .Where(c => !c.name.StartsWith("__preview__")).ToDictionary(c => c.name);
        }

        [MenuItem("Tools/uHand/Build Animator Controller")]
        public static void Build()
        {
            var manifest = UHandPaths.LoadManifest();
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(UHandPaths.Fbx);
            if (model == null) throw new FileNotFoundException("FBX が無い: " + UHandPaths.Fbx);
            var clips = LoadClips();
            var missing = manifest.clips.Where(c => !clips.ContainsKey(c.name)).Select(c => c.name).ToArray();
            if (missing.Length > 0) throw new Exception("FBX に無いクリップがある: " + string.Join(", ", missing));

            AssetDatabase.DeleteAsset(UHandPaths.Controller);
            if (AssetDatabase.IsValidFolder(UHandPaths.Masks)) AssetDatabase.DeleteAsset(UHandPaths.Masks);
            AssetDatabase.CreateFolder(UHandPaths.Dir, "Masks");
            var ctrl = AnimatorController.CreateAnimatorControllerAtPath(UHandPaths.Controller);

            // 層 0: クリップの再生。何も再生していないときは rest（形のままの姿勢）
            var sm = ctrl.layers[0].stateMachine;
            sm.defaultState = sm.AddState("rest");
            foreach (var c in manifest.clips.Where(c => !c.name.StartsWith("dof_")))
                sm.AddState(c.name).motion = clips[c.name];

            // 量ごとの層。クリップ dof_<量> を、同じ名前の数値（0〜1）で時刻を引く
            foreach (var dof in manifest.dof_list)
            {
                ctrl.AddParameter(dof.name, AnimatorControllerParameterType.Float);
                var mask = new AvatarMask { name = "UHand_" + dof.name };
                mask.AddTransformPath(model.transform, true);
                var bones = new HashSet<string>(dof.bones);
                for (int i = 0; i < mask.transformCount; i++)
                {
                    string path = mask.GetTransformPath(i);
                    mask.SetTransformActive(i, bones.Contains(path.Substring(path.LastIndexOf('/') + 1)));
                }
                AssetDatabase.CreateAsset(mask, UHandPaths.Masks + "/UHand_" + dof.name + ".mask");

                var lsm = new AnimatorStateMachine { name = "dof_" + dof.name, hideFlags = HideFlags.HideInHierarchy };
                AssetDatabase.AddObjectToAsset(lsm, UHandPaths.Controller);
                var st = lsm.AddState("drive");
                st.motion = clips[dof.clip];
                st.timeParameterActive = true;
                st.timeParameter = dof.name;
                ctrl.AddLayer(new AnimatorControllerLayer
                {
                    name = "dof_" + dof.name, defaultWeight = 0f, avatarMask = mask,
                    blendingMode = AnimatorLayerBlendingMode.Override, stateMachine = lsm,
                });
            }
            EditorUtility.SetDirty(ctrl);

            var go = (GameObject)PrefabUtility.InstantiatePrefab(model);
            var anim = go.GetComponent<Animator>();
            if (anim == null) anim = go.AddComponent<Animator>();
            anim.runtimeAnimatorController = ctrl;
            if (go.GetComponent<UHandDriver>() == null) go.AddComponent<UHandDriver>();
            PrefabUtility.SaveAsPrefabAsset(go, UHandPaths.Prefab);
            UnityEngine.Object.DestroyImmediate(go);
            AssetDatabase.SaveAssets();
            Debug.Log($"[uHand] controller を作った: クリップ {manifest.clips.Length} 本、量の層 {manifest.dof_list.Length} 枚");
        }

        static Transform Find(Transform root, string name)
        {
            return root.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name);
        }

        // 目録の目印と比べる。返り値は (目印の数, 外れた数, 最大のずれ [mm]) と 1 行ずつの記録
        public static (int total, int bad, float worst, List<string> lines) Check(float tolMm = 0.5f)
        {
            var manifest = UHandPaths.LoadManifest();
            var clips = LoadClips();
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(UHandPaths.Prefab);
            if (prefab == null) throw new FileNotFoundException("プレハブが無い。先に Build を実行する: " + UHandPaths.Prefab);
            var go = UnityEngine.Object.Instantiate(prefab);
            var anim = go.GetComponent<Animator>();
            var lines = new List<string>();
            int bad = 0;
            float worst = 0f;
            try
            {
                foreach (var p in manifest.probes)
                {
                    if (p.kind == "clip")
                    {
                        clips[p.clip].SampleAnimation(go, p.time);
                    }
                    else
                    {
                        // 量から: Animator の層で引く（実行時と同じ経路）
                        anim.Rebind();
                        for (int i = 0; i < manifest.dof_list.Length; i++)
                        {
                            var d = manifest.dof_list[i];
                            anim.SetLayerWeight(anim.GetLayerIndex("dof_" + d.name), 1f);
                            anim.SetFloat(d.name, Mathf.InverseLerp(d.min, d.max, p.values[i]));
                        }
                        anim.Update(0f);
                        anim.Update(0f);
                    }
                    var a = Find(go.transform, p.a);
                    var b = Find(go.transform, p.b);
                    if (a == null || b == null) throw new Exception($"骨が無い: {p.a} / {p.b}");
                    float got = Vector3.Distance(a.position, b.position);
                    float errMm = Mathf.Abs(got - p.dist) * 1000f;
                    worst = Mathf.Max(worst, errMm);
                    if (errMm > tolMm) bad++;
                    string what = p.kind == "clip" ? $"{p.clip}@{p.time:0.00}s" : "dofs[" + string.Join(",", p.values.Select(v => v.ToString("0.##"))) + "]";
                    lines.Add($"{(errMm > tolMm ? "NG" : "ok")} {what} {p.a}-{p.b} expected {p.dist * 1000f:0.00}mm got {got * 1000f:0.00}mm");
                }
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(go);
            }
            return (manifest.probes.Length, bad, worst, lines);
        }

        [MenuItem("Tools/uHand/Verify")]
        public static void Verify()
        {
            var r = Check();
            foreach (var l in r.lines) Debug.Log("[uHand] " + l);
            Debug.Log($"[uHand] 目印 {r.total} 個のうち外れ {r.bad} 個、最大のずれ {r.worst:0.000} mm");
        }

        // batchmode 用: 組み立てて確かめ、結果を uhand_verify.txt に書いて終わる
        public static void BuildAndVerifyBatch()
        {
            int code = 1;
            var log = new List<string>();
            try
            {
                AssetDatabase.Refresh();
                Build();
                var r = Check();
                log.AddRange(r.lines);
                log.Add($"total {r.total} bad {r.bad} worst_mm {r.worst:0.000}");
                var clips = LoadClips();
                log.Add("clips " + string.Join(",", clips.Keys.OrderBy(k => k)));
                log.Add("loop " + string.Join(",", clips.Values.Where(c => c.isLooping).Select(c => c.name).OrderBy(k => k)));
                code = r.bad == 0 ? 0 : 2;
            }
            catch (Exception e)
            {
                log.Add("EXCEPTION " + e);
            }
            File.WriteAllLines("uhand_verify.txt", log);
            EditorApplication.Exit(code);
        }
    }
}
