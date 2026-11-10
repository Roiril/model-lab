// uHand を実行時に動かす。Tools > uHand > Build Animator Controller が作るプレハブに付いている。
//
// 使い方は 2 通り。
//   クリップを再生する:  driver.Play("open_close");
//   サーボ 6 個ぶんの量を直接決める:  driver.SetPose(little: 1f, ring: 1f, middle: 1f, index: 0f, thumb: 0.9f, wrist: 0f);
// 量は 0（開く）〜 1（握る）。手首だけ -1 〜 1。Inspector のつまみからも動かせる（mode を Manual にする）。
// 指は量 1 個から 3 つの関節と銀の板の姿勢が決まる（Blender 側で機構を解いて焼いてある）。
using UnityEngine;

namespace UHand
{
    [RequireComponent(typeof(Animator))]
    public class UHandDriver : MonoBehaviour
    {
        public enum Mode { Gesture, Manual }

        public Mode mode = Mode.Gesture;
        [Tooltip("再生するクリップの名前（Gesture のとき）。空なら形のままの姿勢")]
        public string gesture = "idle";
        [Tooltip("クリップを切り替えるときに混ぜる時間 [秒]")]
        public float crossFade = 0.15f;

        [Header("サーボ 6 個ぶんの量（Manual のとき）")]
        [Range(0f, 1f)] public float little;
        [Range(0f, 1f)] public float ring;
        [Range(0f, 1f)] public float middle;
        [Range(0f, 1f)] public float index;
        [Range(0f, 1f)] public float thumb;
        [Range(-1f, 1f)] public float wrist;

        static readonly string[] Dofs = { "little", "ring", "middle", "index", "thumb", "wrist" };
        Animator anim;
        int[] layers;
        string playing;

        void Awake()
        {
            anim = GetComponent<Animator>();
            layers = new int[Dofs.Length];
            for (int i = 0; i < Dofs.Length; i++) layers[i] = anim.GetLayerIndex("dof_" + Dofs[i]);
        }

        void OnEnable()
        {
            playing = null;
        }

        void Update()
        {
            bool manual = mode == Mode.Manual;
            for (int i = 0; i < layers.Length; i++)
                if (layers[i] >= 0) anim.SetLayerWeight(layers[i], manual ? 1f : 0f);
            anim.SetFloat("little", little);
            anim.SetFloat("ring", ring);
            anim.SetFloat("middle", middle);
            anim.SetFloat("index", index);
            anim.SetFloat("thumb", thumb);
            anim.SetFloat("wrist", (wrist + 1f) * 0.5f);     // クリップの時刻は 0〜1 で引く
            if (manual)
            {
                playing = null;
                return;
            }
            string want = string.IsNullOrEmpty(gesture) ? "rest" : gesture;
            if (want != playing)
            {
                anim.CrossFadeInFixedTime(want, crossFade, 0);
                playing = want;
            }
        }

        /// <summary>クリップを再生する。同じ名前でも頭から再生し直す。</summary>
        public void Play(string clip)
        {
            mode = Mode.Gesture;
            gesture = clip;
            playing = null;
        }

        /// <summary>サーボ 6 個ぶんの量を直接決める。</summary>
        public void SetPose(float little, float ring, float middle, float index, float thumb, float wrist = 0f)
        {
            mode = Mode.Manual;
            this.little = Mathf.Clamp01(little);
            this.ring = Mathf.Clamp01(ring);
            this.middle = Mathf.Clamp01(middle);
            this.index = Mathf.Clamp01(index);
            this.thumb = Mathf.Clamp01(thumb);
            this.wrist = Mathf.Clamp(wrist, -1f, 1f);
        }
    }
}
