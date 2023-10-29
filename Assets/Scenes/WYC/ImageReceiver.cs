using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public class ImageReceiver : MonoBehaviour
{
    public string serverUrl = "http://127.0.0.1:8000/unity_connect/send_image/";

    void Start()
    {
        StartCoroutine(SendRequest("��"));
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

            // �ؽ�ó�� �޸𸮿� ����
            texture.Apply();

            // �ؽ�ó ��� �� ����
            Destroy(texture);
        }
    }
}
