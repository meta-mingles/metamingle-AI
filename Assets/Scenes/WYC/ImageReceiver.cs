using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public class ImageReceiver : MonoBehaviour
{
    public string serverUrl = "http://127.0.0.1:8000/unity_connect/send_image/";

    void Start()
    {
        StartCoroutine(SendRequest("말"));
    }

    IEnumerator SendRequest(string requestStr)
    {
        WWWForm form = new WWWForm();
        form.AddField("request_str", requestStr);
        UnityWebRequest request = UnityWebRequest.Post(serverUrl, form);
        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.error);
        }
        else
        {
            byte[] imageData = request.downloadHandler.data;
            Texture2D texture = new Texture2D(2, 2);
            texture.LoadImage(imageData);

            // 텍스처를 메모리에 적용
            texture.Apply();

            // 텍스처 사용 후 해제
            Destroy(texture);
        }
    }
}
