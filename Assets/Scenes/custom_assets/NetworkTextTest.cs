// NetworkTextTest.cs
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using System.Text;

public class NetworkTextTest : MonoBehaviour
{
    private string apiUrl = "http://192.168.0.17:8000/chatbot/test_text"; // FastAPI ������ ��������Ʈ URL�� �Է��ϼ���.

    void Start()
    {
        // JSON ������ ����
        string json = "{\"text\":\"Text Test Hi!\"}";

        // JSON �����͸� ����Ʈ �迭�� ��ȯ
        byte[] jsonData = Encoding.UTF8.GetBytes(json);

        StartCoroutine(PostJson(jsonData));
    }

    IEnumerator PostJson(byte[] jsonData)
    {
        using (UnityWebRequest www = new UnityWebRequest(apiUrl, "POST"))
        {
            www.uploadHandler = new UploadHandlerRaw(jsonData);
            www.downloadHandler = new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");

            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError(www.error);
            }
            else
            {
                string responseText = www.downloadHandler.text;
                Debug.Log("Response from server: " + responseText);

                // ���⿡�� responseText�� �Ľ��Ͽ� ������� ����
            }
        }
    }
}
